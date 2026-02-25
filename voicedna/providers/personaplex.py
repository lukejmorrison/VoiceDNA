from __future__ import annotations

import io
import importlib
import os
import threading
import wave
from dataclasses import dataclass
from typing import Any

import numpy as np


def get_personaplex_min_vram_gb() -> float:
    raw_value = os.getenv("VOICEDNA_MIN_PERSONAPLEX_VRAM_GB", "12")
    try:
        return float(raw_value)
    except ValueError:
        return 12.0


def detect_vram_gb() -> float | None:
    simulated = os.getenv("VOICEDNA_SIMULATED_VRAM_GB")
    if simulated:
        try:
            return float(simulated)
        except ValueError:
            pass

    try:
        torch = importlib.import_module("torch")
        if not torch.cuda.is_available():
            return None
        current_index = torch.cuda.current_device()
        props = torch.cuda.get_device_properties(current_index)
        return float(props.total_memory) / (1024.0**3)
    except Exception:
        return None


@dataclass
class PersonaPlexConfig:
    model_id: str = "nvidia/personaplex-7b-v1"
    device: str = "auto"
    torch_dtype: str = "auto"


class PersonaPlexTTS:
    _pipeline_lock = threading.Lock()
    _shared_pipeline: Any | None = None
    _shared_signature: tuple[str, str, str] | None = None

    def __init__(
        self,
        model_id: str = "nvidia/personaplex-7b-v1",
        device: str = "auto",
        torch_dtype: str = "auto",
    ):
        self.config = PersonaPlexConfig(model_id=model_id, device=device, torch_dtype=torch_dtype)
        self._ensure_pipeline_loaded()

    def _ensure_pipeline_loaded(self) -> None:
        signature = (self.config.model_id, self.config.device, self.config.torch_dtype)
        if PersonaPlexTTS._shared_pipeline is not None and PersonaPlexTTS._shared_signature == signature:
            return

        with PersonaPlexTTS._pipeline_lock:
            if PersonaPlexTTS._shared_pipeline is not None and PersonaPlexTTS._shared_signature == signature:
                return

            try:
                torch = importlib.import_module("torch")
                transformers = importlib.import_module("transformers")
                pipeline = getattr(transformers, "pipeline")
            except Exception as error:
                raise RuntimeError(
                    "PersonaPlex backend dependencies are missing. Install with: pip install \"voicedna[personaplex]\""
                ) from error

            transformers_version = str(getattr(transformers, "__version__", ""))
            major_token = transformers_version.split(".", maxsplit=1)[0]
            if major_token.isdigit() and int(major_token) >= 5:
                raise RuntimeError(
                    "PersonaPlex currently supports transformers 4.x. "
                    f"Detected transformers=={transformers_version}. "
                    "Install a compatible version with: pip install 'transformers<5'"
                )

            pipeline_device = -1
            if self.config.device == "auto":
                pipeline_device = 0 if torch.cuda.is_available() else -1
            elif self.config.device.startswith("cuda"):
                pipeline_device = 0

            min_vram_gb = get_personaplex_min_vram_gb()
            detected_vram_gb = detect_vram_gb()
            if detected_vram_gb is not None and detected_vram_gb < min_vram_gb:
                raise RuntimeError(
                    f"Detected {detected_vram_gb:.1f}GB VRAM, but PersonaPlex requires at least {min_vram_gb:.1f}GB."
                )

            dtype = "auto"
            if self.config.torch_dtype != "auto":
                try:
                    dtype = getattr(torch, self.config.torch_dtype)
                except Exception:
                    dtype = "auto"

            try:
                PersonaPlexTTS._shared_pipeline = pipeline(
                    task="text-to-speech",
                    model=self.config.model_id,
                    device=pipeline_device,
                    torch_dtype=dtype,
                )
                PersonaPlexTTS._shared_signature = signature
            except Exception as error:
                raise RuntimeError(
                    "Failed to initialize PersonaPlex TTS pipeline. "
                    "Verify model availability, transformers compatibility (4.x), and GPU/VRAM requirements for "
                    "nvidia/personaplex-7b-v1. "
                    f"Original error: {error}"
                ) from error

    @property
    def pipeline(self) -> Any:
        self._ensure_pipeline_loaded()
        if PersonaPlexTTS._shared_pipeline is None:
            raise RuntimeError("PersonaPlex pipeline was not initialized")
        return PersonaPlexTTS._shared_pipeline

    def synthesize(self, text: str, sample_rate: int = 24000) -> bytes:
        if not text or not text.strip():
            raise ValueError("Text for PersonaPlex synthesis must not be empty")

        result = self.pipeline(text)
        audio = result.get("audio") if isinstance(result, dict) else None
        result_rate = result.get("sampling_rate", sample_rate) if isinstance(result, dict) else sample_rate

        if audio is None:
            raise RuntimeError("PersonaPlex pipeline returned no audio payload")

        return self._to_wav_bytes(audio, int(result_rate))

    def _to_wav_bytes(self, audio: Any, sample_rate: int) -> bytes:
        samples = np.asarray(audio, dtype=np.float32).reshape(-1)
        samples = np.clip(samples, -1.0, 1.0)
        pcm = (samples * 32767.0).astype(np.int16)

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wave_file:
            wave_file.setnchannels(1)
            wave_file.setsampwidth(2)
            wave_file.setframerate(sample_rate)
            wave_file.writeframes(pcm.tobytes())
        return buffer.getvalue()
