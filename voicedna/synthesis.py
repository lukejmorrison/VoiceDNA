from __future__ import annotations

import io
import math
import os
import struct
import subprocess
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

from voice_dna import VoiceDNA

from .framework import VoiceDNAProcessor
from .providers import PersonaPlexTTS, PiperTTS
from .providers.personaplex import describe_personaplex_vram
from .providers.piper import piper_natural_message


def is_omarchy_environment() -> bool:
    if Path("/etc/omarchy-release").exists():
        return True
    if Path.home().joinpath(".config/omarchy").exists():
        return True
    desktop = os.getenv("XDG_CURRENT_DESKTOP", "").lower()
    if "omarchy" in desktop or "hyprland" in desktop:
        return True
    return False


def resolve_tts_backend(requested_backend: str, natural_voice: bool = False) -> str:
    backend = (requested_backend or "auto").strip().lower()

    if backend == "auto":
        if natural_voice or is_omarchy_environment():
            return "natural_auto"
        return "simple"

    if backend in {"personaplex", "piper", "simple", "elevenlabs", "xtts", "cartesia", "natural_auto"}:
        if backend in {"elevenlabs", "xtts", "cartesia"}:
            return "simple"
        return backend

    raise ValueError(
        f"Unsupported backend '{requested_backend}'. Use one of: auto, personaplex, piper, simple, elevenlabs, xtts, cartesia"
    )


@dataclass
class NaturalBackendDecision:
    backend: str
    status_message: str
    color: str
    detected_vram_gb: float | None
    required_vram_gb: float
    recommendation: str | None = None


def detect_natural_backend_decision() -> NaturalBackendDecision:
    detected_vram_gb, min_vram_gb, vram_status, status_color = describe_personaplex_vram()

    if detected_vram_gb is None:
        return NaturalBackendDecision(
            backend="piper",
            status_message=f"{vram_status} -> using Piper natural voice.",
            color=status_color,
            detected_vram_gb=None,
            required_vram_gb=min_vram_gb,
            recommendation=(
                "For full PersonaPlex quality, upgrade to 24GB+ card or use cloud proxy."
            ),
        )

    if detected_vram_gb < min_vram_gb:
        return NaturalBackendDecision(
            backend="piper",
            status_message=(
                f"Detected {detected_vram_gb:.1f}GB VRAM -> using Piper natural voice "
                f"(PersonaPlex target: {min_vram_gb:.1f}GB+)."
            ),
            color=status_color,
            detected_vram_gb=detected_vram_gb,
            required_vram_gb=min_vram_gb,
            recommendation=(
                "For full PersonaPlex quality, upgrade to 24GB+ card or use cloud proxy."
            ),
        )

    return NaturalBackendDecision(
        backend="personaplex",
        status_message=f"Detected {detected_vram_gb:.1f}GB VRAM -> using PersonaPlex natural voice.",
        color="green",
        detected_vram_gb=detected_vram_gb,
        required_vram_gb=min_vram_gb,
    )


def select_natural_backend() -> tuple[str, str]:
    decision = detect_natural_backend_decision()
    return decision.backend, decision.status_message


class _SimpleLocalTTS:
    def synthesize(self, text: str, sample_rate: int = 22050) -> bytes:
        if not text or not text.strip():
            raise ValueError("Text for synthesis must not be empty")

        if self._espeak_available():
            return self._synthesize_with_espeak(text)
        return self._synthesize_with_tone(text, sample_rate=sample_rate)

    def _espeak_available(self) -> bool:
        return subprocess.call(
            ["sh", "-c", "command -v espeak-ng >/dev/null 2>&1"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ) == 0

    def _synthesize_with_espeak(self, text: str) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
            wav_path = Path(handle.name)

        try:
            completed = subprocess.run(
                ["espeak-ng", "-w", str(wav_path), text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr.strip() or "espeak-ng failed")
            return wav_path.read_bytes()
        finally:
            wav_path.unlink(missing_ok=True)

    def _synthesize_with_tone(self, text: str, sample_rate: int = 22050) -> bytes:
        duration_seconds = max(0.6, min(4.0, 0.06 * len(text)))
        frequency = 220.0
        amplitude = 0.18

        frame_count = int(duration_seconds * sample_rate)
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for index in range(frame_count):
                value = int(32767.0 * amplitude * math.sin(2.0 * math.pi * frequency * index / sample_rate))
                wav_file.writeframesraw(struct.pack("<h", value))
        return buffer.getvalue()


def _build_provider(backend: str) -> Any:
    if backend == "personaplex":
        return PersonaPlexTTS(
            model_id=os.getenv("VOICEDNA_PERSONAPLEX_MODEL", "nvidia/personaplex-7b-v1"),
            device=os.getenv("VOICEDNA_PERSONAPLEX_DEVICE", "auto"),
            torch_dtype=os.getenv("VOICEDNA_PERSONAPLEX_DTYPE", "auto"),
        )
    if backend == "piper":
        return PiperTTS(
            model_path=os.getenv("VOICEDNA_PIPER_MODEL", ""),
            executable=os.getenv("VOICEDNA_PIPER_EXECUTABLE", "piper"),
            speaker_id=os.getenv("VOICEDNA_PIPER_SPEAKER", ""),
        )
    return _SimpleLocalTTS()


def synthesize_and_process(
    text: str,
    dna: VoiceDNA,
    backend: str = "auto",
    natural_voice: bool = False,
    params: Dict[str, Any] | None = None,
) -> Tuple[bytes, Dict[str, Any], str]:
    resolved_backend = resolve_tts_backend(backend, natural_voice=natural_voice)
    natural_backend_status: str | None = None
    natural_backend_color: str | None = None
    recommendation: str | None = None
    detected_vram_gb: float | None = None
    required_vram_gb: float | None = None

    if resolved_backend == "natural_auto":
        decision = detect_natural_backend_decision()
        resolved_backend = decision.backend
        natural_backend_status = decision.status_message
        natural_backend_color = decision.color
        recommendation = decision.recommendation
        detected_vram_gb = decision.detected_vram_gb
        required_vram_gb = decision.required_vram_gb

    try:
        provider = _build_provider(resolved_backend)
    except Exception as error:
        if resolved_backend == "piper":
            natural_backend_status = (
                f"{piper_natural_message()} unavailable ({error}) -> falling back to simple local voice."
            )
            natural_backend_color = "yellow"
            resolved_backend = "simple"
            provider = _build_provider(resolved_backend)
        else:
            raise

    processor = VoiceDNAProcessor()
    process_params: Dict[str, Any] = {
        "text": text,
        "audio_format": "wav",
        "base_model": resolved_backend,
        "imprint_converter.mode": os.getenv("VOICEDNA_IMPRINT_MODE", "simple"),
    }
    if params:
        process_params.update(params)

    if natural_backend_status:
        process_params["natural_backend_status"] = natural_backend_status
    if recommendation:
        process_params["natural_backend_recommendation"] = recommendation

    try:
        processed_audio = processor.synthesize_and_process(text=text, dna=dna, tts_provider=provider, params=process_params)
    except Exception as error:
        if resolved_backend == "personaplex":
            fallback_status = f"PersonaPlex unavailable ({error}) -> falling back to Piper natural voice."
            recommendation = "For full PersonaPlex quality, upgrade to 24GB+ card or use cloud proxy."
            try:
                fallback_provider = _build_provider("piper")
                process_params["base_model"] = "piper"
                process_params["natural_backend_status"] = fallback_status
                process_params["natural_backend_recommendation"] = recommendation
                processed_audio = processor.synthesize_and_process(
                    text=text,
                    dna=dna,
                    tts_provider=fallback_provider,
                    params=process_params,
                )
                resolved_backend = "piper"
                natural_backend_status = fallback_status
                natural_backend_color = "yellow"
            except Exception as fallback_error:
                final_status = (
                    f"{fallback_status} Piper unavailable ({fallback_error}) -> falling back to simple local voice."
                )
                simple_provider = _build_provider("simple")
                process_params["base_model"] = "simple"
                process_params["natural_backend_status"] = final_status
                process_params["natural_backend_recommendation"] = recommendation
                processed_audio = processor.synthesize_and_process(
                    text=text,
                    dna=dna,
                    tts_provider=simple_provider,
                    params=process_params,
                )
                resolved_backend = "simple"
                natural_backend_status = final_status
                natural_backend_color = "yellow"
        else:
            raise

    report = processor.get_last_report()
    if natural_backend_status:
        report["natural_backend_status"] = natural_backend_status
    if natural_backend_color:
        report["natural_backend_color"] = natural_backend_color
    if recommendation:
        report["natural_backend_recommendation"] = recommendation
    if detected_vram_gb is not None:
        report["detected_vram_gb"] = round(detected_vram_gb, 2)
    if required_vram_gb is not None:
        report["required_vram_gb"] = round(required_vram_gb, 2)
    report["resolved_backend"] = resolved_backend
    return processed_audio, report, resolved_backend


def play_wav_bytes(audio_bytes: bytes) -> str:
    if not audio_bytes:
        raise ValueError("No audio bytes provided for playback")

    try:
        from pydub import AudioSegment
        from pydub.playback import play

        segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
        play(segment)
        return "pydub"
    except Exception:
        pass

    try:
        import numpy as np
        import sounddevice as sd

        with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            frame_count = wav_file.getnframes()
            raw_frames = wav_file.readframes(frame_count)

        if sample_width != 2:
            raise RuntimeError("Only 16-bit PCM WAV playback is supported for sounddevice fallback")

        samples = np.frombuffer(raw_frames, dtype=np.int16)
        if channels > 1:
            samples = samples.reshape(-1, channels)

        sd.play(samples, samplerate=sample_rate)
        sd.wait()
        return "sounddevice"
    except Exception:
        pass

    for player in (("pw-play", ["pw-play", "-"]), ("aplay", ["aplay", "-"])):
        name, command = player
        if subprocess.call(
            ["sh", "-c", f"command -v {name} >/dev/null 2>&1"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ) != 0:
            continue

        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        assert process.stdin is not None
        process.stdin.write(audio_bytes)
        process.stdin.close()
        process.wait(timeout=20)
        return name

    raise RuntimeError(
        "No audio playback backend available. Install pydub/audioop-lts, sounddevice, or PipeWire/ALSA playback tools (pw-play/aplay)."
    )
