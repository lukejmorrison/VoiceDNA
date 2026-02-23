from __future__ import annotations

import io
import wave

import numpy as np


def decode_wav_bytes(audio_bytes: bytes) -> tuple[int, np.ndarray]:
    with wave.open(io.BytesIO(audio_bytes), "rb") as wave_file:
        channels = wave_file.getnchannels()
        sample_width = wave_file.getsampwidth()
        sample_rate = wave_file.getframerate()
        frame_count = wave_file.getnframes()
        raw_frames = wave_file.readframes(frame_count)

    if sample_width != 2:
        raise ValueError("Only 16-bit PCM WAV is supported by fallback path")

    samples = np.frombuffer(raw_frames, dtype=np.int16)
    if channels > 1:
        samples = samples.reshape(-1, channels)
    return sample_rate, samples


def encode_wav_bytes(sample_rate: int, samples: np.ndarray) -> bytes:
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


def pitch_shift_wav_bytes(audio_bytes: bytes, pitch_factor: float) -> bytes:
    sample_rate, samples = decode_wav_bytes(audio_bytes)

    if samples.ndim == 1:
        shifted = _resample_1d(samples, pitch_factor)
    else:
        shifted_channels = [_resample_1d(samples[:, channel_index], pitch_factor) for channel_index in range(samples.shape[1])]
        shifted = np.stack(shifted_channels, axis=1)

    return encode_wav_bytes(sample_rate, shifted)


def imprint_mix_wav_bytes(audio_bytes: bytes, strength: float) -> bytes:
    sample_rate, samples = decode_wav_bytes(audio_bytes)
    bounded_strength = max(0.0, min(1.0, strength))
    wet_gain = 0.2 + 0.8 * bounded_strength
    mixed = samples.astype(np.float32) * (1.0 - bounded_strength * 0.35) + samples.astype(np.float32) * wet_gain * 0.35
    return encode_wav_bytes(sample_rate, mixed)


def _resample_1d(signal: np.ndarray, pitch_factor: float) -> np.ndarray:
    bounded_factor = max(0.5, min(1.25, pitch_factor))
    source = signal.astype(np.float32)
    old_indices = np.arange(source.shape[0], dtype=np.float32)
    target_length = max(1, int(source.shape[0] / bounded_factor))
    new_indices = np.linspace(0, source.shape[0] - 1, target_length, dtype=np.float32)
    resampled = np.interp(new_indices, old_indices, source)

    restore_indices = np.linspace(0, resampled.shape[0] - 1, source.shape[0], dtype=np.float32)
    restored = np.interp(restore_indices, np.arange(resampled.shape[0], dtype=np.float32), resampled)
    return np.clip(restored, -32768, 32767).astype(np.int16)
