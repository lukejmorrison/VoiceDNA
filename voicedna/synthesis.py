from __future__ import annotations

import io
import math
import os
import struct
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Any, Dict, Tuple

from voice_dna import VoiceDNA

from .framework import VoiceDNAProcessor
from .providers import PersonaPlexTTS


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
            return "personaplex"
        return "simple"

    if backend in {"personaplex", "simple", "elevenlabs", "xtts", "cartesia"}:
        if backend in {"elevenlabs", "xtts", "cartesia"}:
            return "simple"
        return backend

    raise ValueError(
        f"Unsupported backend '{requested_backend}'. Use one of: auto, personaplex, simple, elevenlabs, xtts, cartesia"
    )


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
    return _SimpleLocalTTS()


def synthesize_and_process(
    text: str,
    dna: VoiceDNA,
    backend: str = "auto",
    natural_voice: bool = False,
    params: Dict[str, Any] | None = None,
) -> Tuple[bytes, Dict[str, Any], str]:
    resolved_backend = resolve_tts_backend(backend, natural_voice=natural_voice)
    provider = _build_provider(resolved_backend)

    processor = VoiceDNAProcessor()
    process_params: Dict[str, Any] = {
        "text": text,
        "audio_format": "wav",
        "base_model": resolved_backend,
        "imprint_converter.mode": os.getenv("VOICEDNA_IMPRINT_MODE", "simple"),
    }
    if params:
        process_params.update(params)

    processed_audio = processor.synthesize_and_process(text=text, dna=dna, tts_provider=provider, params=process_params)
    return processed_audio, processor.get_last_report(), resolved_backend


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
        "No audio playback backend available. Install pydub-compatible stack or PipeWire/ALSA playback tools (pw-play/aplay)."
    )
