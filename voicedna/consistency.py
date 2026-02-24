from __future__ import annotations

import hashlib
import io
import math
import wave
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    left_array = np.asarray(left, dtype=np.float32)
    right_array = np.asarray(right, dtype=np.float32)
    if left_array.size == 0 or right_array.size == 0:
        return 0.0
    if left_array.shape != right_array.shape:
        min_size = min(left_array.size, right_array.size)
        left_array = left_array[:min_size]
        right_array = right_array[:min_size]

    left_norm = float(np.linalg.norm(left_array))
    right_norm = float(np.linalg.norm(right_array))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return float(np.dot(left_array, right_array) / (left_norm * right_norm))


def _fit_embedding_dims(values: Iterable[float], dims: int = 256) -> list[float]:
    array = np.asarray(list(values), dtype=np.float32)
    if array.size == 0:
        return [0.0] * dims
    if array.size == dims:
        return array.tolist()

    old_positions = np.linspace(0.0, 1.0, num=array.size, dtype=np.float32)
    new_positions = np.linspace(0.0, 1.0, num=dims, dtype=np.float32)
    resized = np.interp(new_positions, old_positions, array)
    return resized.astype(np.float32).tolist()


def _legacy_embedding_from_text(imprint_source: str, dims: int = 256) -> list[float]:
    chunks: list[float] = []
    seed = imprint_source.encode("utf-8")
    counter = 0
    while len(chunks) < dims:
        digest = hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
        for offset in range(0, len(digest), 2):
            value = int.from_bytes(digest[offset:offset + 2], "big")
            chunks.append((value / 32767.5) - 1.0)
            if len(chunks) >= dims:
                break
        counter += 1
    return chunks[:dims]


def _read_wav_bytes(audio_bytes: bytes) -> tuple[int, np.ndarray]:
    with wave.open(io.BytesIO(audio_bytes), "rb") as wave_file:
        channels = wave_file.getnchannels()
        sample_width = wave_file.getsampwidth()
        sample_rate = wave_file.getframerate()
        frame_count = wave_file.getnframes()
        raw_frames = wave_file.readframes(frame_count)

    if sample_width != 2:
        raise ValueError("Only 16-bit PCM WAV is supported for consistency extraction")

    samples = np.frombuffer(raw_frames, dtype=np.int16).astype(np.float32)
    if channels > 1:
        samples = samples.reshape(-1, channels).mean(axis=1)
    return sample_rate, samples


def _decode_wav_bytes(audio_bytes: bytes) -> tuple[int, np.ndarray]:
    sample_rate, mono = _read_wav_bytes(audio_bytes)
    return sample_rate, mono.astype(np.int16)


def _encode_wav_bytes(sample_rate: int, samples: np.ndarray) -> bytes:
    output = io.BytesIO()
    cast_samples = np.asarray(samples)
    if cast_samples.dtype != np.int16:
        cast_samples = np.clip(cast_samples, -32768, 32767).astype(np.int16)

    channels = 1 if cast_samples.ndim == 1 else cast_samples.shape[1]
    with wave.open(output, "wb") as wave_file:
        wave_file.setnchannels(channels)
        wave_file.setsampwidth(2)
        wave_file.setframerate(sample_rate)
        wave_file.writeframes(cast_samples.tobytes())
    return output.getvalue()


class VoiceConsistencyEngine:
    def __init__(
        self,
        threshold: float = 0.92,
        correction_strength: float = 0.10,
        watermark_depth: float = 0.002,
    ):
        self.threshold = threshold
        self.correction_strength = correction_strength
        self.watermark_depth = watermark_depth

    def extract_embedding_from_imprint(self, imprint_source: str, dims: int = 256) -> list[float]:
        path = Path(imprint_source)
        if path.exists() and path.is_file():
            try:
                return self.extract_embedding_from_audio(path.read_bytes(), dims=dims)
            except Exception:
                pass
        return _legacy_embedding_from_text(imprint_source, dims=dims)

    def extract_embedding_from_audio(self, audio_bytes: bytes, dims: int = 256) -> list[float]:
        for extractor in (self._extract_with_resemblyzer, self._extract_with_speechbrain, self._extract_with_numpy):
            try:
                embedding = extractor(audio_bytes, dims)
                if embedding and len(embedding) > 0:
                    return _fit_embedding_dims(embedding, dims=dims)
            except Exception:
                continue
        return [0.0] * dims

    def enforce_consistency(
        self,
        audio_bytes: bytes,
        core_embedding: Sequence[float],
        voice_fingerprint_id: str,
    ) -> tuple[bytes, float, bool, bool]:
        current_embedding = self.extract_embedding_from_audio(audio_bytes, dims=len(core_embedding) or 256)
        score = cosine_similarity(current_embedding, core_embedding)
        corrected = audio_bytes
        correction_applied = False

        if score < self.threshold:
            correction_ratio = max(0.0, min(1.0, (self.threshold - score) * (1.0 + self.correction_strength)))
            corrected = self._apply_parametric_correction(audio_bytes, correction_ratio)
            correction_applied = corrected != audio_bytes
            if correction_applied:
                corrected_embedding = self.extract_embedding_from_audio(corrected, dims=len(core_embedding) or 256)
                score = max(score, cosine_similarity(corrected_embedding, core_embedding))

        watermarked = self.apply_sonic_watermark(corrected, voice_fingerprint_id)
        rvc_ready = score >= self.threshold
        return watermarked, score, rvc_ready, correction_applied

    def apply_sonic_watermark(self, audio_bytes: bytes, voice_fingerprint_id: str) -> bytes:
        try:
            sample_rate, samples = _decode_wav_bytes(audio_bytes)
        except Exception:
            return audio_bytes

        if samples.size == 0:
            return audio_bytes

        bit_stream = self._fingerprint_bits(voice_fingerprint_id)
        watermark = self._build_watermark_signal(samples.shape[0], sample_rate, bit_stream)

        if samples.ndim == 1:
            mixed = samples.astype(np.float32) + watermark
        else:
            mixed = samples.astype(np.float32) + watermark[:, None]

        return _encode_wav_bytes(sample_rate, mixed)

    def _extract_with_resemblyzer(self, audio_bytes: bytes, dims: int) -> list[float]:
        from resemblyzer import VoiceEncoder, preprocess_wav

        sample_rate, mono = _read_wav_bytes(audio_bytes)
        waveform = mono / 32768.0
        processed = preprocess_wav(waveform, source_sr=sample_rate)
        embedding = VoiceEncoder().embed_utterance(processed)
        return _fit_embedding_dims(embedding, dims=dims)

    def _extract_with_speechbrain(self, audio_bytes: bytes, dims: int) -> list[float]:
        import torch
        from speechbrain.pretrained import EncoderClassifier

        sample_rate, mono = _read_wav_bytes(audio_bytes)
        waveform = mono / 32768.0
        if sample_rate != 16000 and waveform.size > 1:
            source = np.linspace(0.0, 1.0, waveform.size, dtype=np.float32)
            target_length = int(waveform.size * (16000 / sample_rate))
            target = np.linspace(0.0, 1.0, max(target_length, 1), dtype=np.float32)
            waveform = np.interp(target, source, waveform)

        classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")
        batch = torch.tensor(waveform, dtype=torch.float32).unsqueeze(0)
        embedding = classifier.encode_batch(batch).detach().cpu().numpy().reshape(-1)
        return _fit_embedding_dims(embedding, dims=dims)

    def _extract_with_numpy(self, audio_bytes: bytes, dims: int) -> list[float]:
        try:
            sample_rate, mono = _read_wav_bytes(audio_bytes)
            mono = mono.astype(np.float32)
            if mono.size == 0:
                return [0.0] * dims
            normalized = mono / 32768.0
            spectrum = np.abs(np.fft.rfft(normalized, n=min(8192, max(512, mono.size))))
            summary = np.concatenate(
                [
                    np.array(
                        [
                            float(np.mean(normalized)),
                            float(np.std(normalized)),
                            float(np.max(np.abs(normalized))),
                            float(sample_rate / 48000.0),
                        ],
                        dtype=np.float32,
                    ),
                    spectrum.astype(np.float32),
                ]
            )
            return _fit_embedding_dims(summary, dims=dims)
        except Exception:
            digest = hashlib.sha256(audio_bytes).digest()
            values = [((digest[index % len(digest)] / 255.0) * 2.0) - 1.0 for index in range(dims)]
            return values

    def _apply_parametric_correction(self, audio_bytes: bytes, correction_ratio: float) -> bytes:
        try:
            sample_rate, samples = _decode_wav_bytes(audio_bytes)
        except Exception:
            return audio_bytes

        bounded = max(0.0, min(1.0, correction_ratio))
        if bounded <= 0.0:
            return audio_bytes

        source = samples.astype(np.float32)
        normalized = source / 32768.0
        shaped = np.tanh(normalized * (1.0 + bounded * 0.6))
        corrected = (1.0 - bounded * 0.35) * normalized + (bounded * 0.35) * shaped
        return _encode_wav_bytes(sample_rate, corrected * 32768.0)

    def _fingerprint_bits(self, voice_fingerprint_id: str) -> list[int]:
        digest = hashlib.sha256(voice_fingerprint_id.encode("utf-8")).digest()
        bits: list[int] = []
        for value in digest:
            for shift in range(8):
                bits.append((value >> shift) & 1)
        return bits

    def _build_watermark_signal(self, sample_count: int, sample_rate: int, bit_stream: Sequence[int]) -> np.ndarray:
        indices = np.arange(sample_count, dtype=np.float32)
        bit_window = max(128, int(sample_rate * 0.015))
        base_frequency = min(7800.0, sample_rate * 0.42)
        signal = np.zeros(sample_count, dtype=np.float32)

        for bit_index, bit in enumerate(bit_stream):
            start = bit_index * bit_window
            if start >= sample_count:
                break
            end = min(sample_count, start + bit_window)
            phase_shift = math.pi / 3 if bit else -math.pi / 3
            carrier = np.sin((2.0 * math.pi * base_frequency * indices[start:end] / sample_rate) + phase_shift)
            signal[start:end] += carrier

        amplitude = 32768.0 * max(0.0, min(0.01, self.watermark_depth))
        return signal * amplitude
