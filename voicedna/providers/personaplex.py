from __future__ import annotations

import io
import importlib
import os
import threading
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_PERSONAPLEX_MODEL = "nvidia/personaplex-7b-v1"
DEFAULT_PERSONAPLEX_LOWVRAM_MODEL = "brianmatzelle/personaplex-7b-v1-bnb-4bit"


def _env_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


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


def describe_personaplex_vram() -> tuple[float | None, float, str, str]:
    detected_vram_gb = detect_vram_gb()
    min_vram_gb = get_personaplex_min_vram_gb()

    if detected_vram_gb is None:
        return None, min_vram_gb, "No CUDA VRAM detected", "yellow"

    if detected_vram_gb < min_vram_gb:
        return (
            detected_vram_gb,
            min_vram_gb,
            f"Detected {detected_vram_gb:.1f}GB VRAM below PersonaPlex target {min_vram_gb:.1f}GB+",
            "yellow",
        )

    return detected_vram_gb, min_vram_gb, f"Detected {detected_vram_gb:.1f}GB VRAM", "green"


def check_personaplex_runtime(low_vram: bool = False) -> tuple[bool, str]:
    try:
        torch = importlib.import_module("torch")
    except Exception:
        return False, "PyTorch is not installed"

    try:
        transformers = importlib.import_module("transformers")
        transformers_version = str(getattr(transformers, "__version__", ""))
        major_token = transformers_version.split(".", maxsplit=1)[0]
        if major_token.isdigit() and int(major_token) >= 5:
            return False, f"transformers {transformers_version} is unsupported; use transformers<5"
    except Exception:
        return False, "transformers is not installed"

    if low_vram:
        try:
            importlib.import_module("bitsandbytes")
        except Exception:
            return False, "bitsandbytes is missing; install voicedna[personaplex-lowvram]"

    if not torch.cuda.is_available():
        return True, "CUDA not available; PersonaPlex can run on CPU (slower)"

    try:
        current_index = torch.cuda.current_device()
        capability = torch.cuda.get_device_capability(current_index)
        capability_value = float(f"{capability[0]}.{capability[1]}")
        arch_list = set(getattr(torch.cuda, "get_arch_list", lambda: [])() or [])
        capability_token = f"sm_{capability[0]}{capability[1]}"

        if arch_list and capability_token not in arch_list:
            return (
                False,
                f"GPU capability {capability_token} is not supported by this PyTorch CUDA build",
            )

        if low_vram and capability_value < 7.0:
            return (
                False,
                f"Low-VRAM PersonaPlex 4-bit mode requires newer CUDA capability; detected sm_{capability[0]}{capability[1]}",
            )
    except Exception:
        return True, "CUDA detected; capability probe unavailable"

    return True, "PersonaPlex runtime dependencies look healthy"


@dataclass
class PersonaPlexConfig:
    model_id: str = DEFAULT_PERSONAPLEX_MODEL
    low_vram_model_id: str = DEFAULT_PERSONAPLEX_LOWVRAM_MODEL
    device: str = "auto"
    torch_dtype: str = "auto"
    low_vram: bool = False
    cpu_offload: bool = True


class PersonaPlexTTS:
    _pipeline_lock = threading.Lock()
    _shared_pipeline: Any | None = None
    _shared_signature: tuple[str, str, str] | None = None

    def __init__(
        self,
        model_id: str = DEFAULT_PERSONAPLEX_MODEL,
        low_vram_model_id: str = DEFAULT_PERSONAPLEX_LOWVRAM_MODEL,
        device: str = "auto",
        torch_dtype: str = "auto",
        low_vram: bool = False,
        cpu_offload: bool = True,
    ):
        self.config = PersonaPlexConfig(
            model_id=model_id,
            low_vram_model_id=low_vram_model_id,
            device=device,
            torch_dtype=torch_dtype,
            low_vram=low_vram,
            cpu_offload=cpu_offload,
        )
        self._ensure_pipeline_loaded()

    def _ensure_pipeline_loaded(self) -> None:
        detected_vram_gb = detect_vram_gb()
        min_vram_gb = get_personaplex_min_vram_gb()
        low_vram_mode = self.config.low_vram or _env_truthy(os.getenv("VOICEDNA_PERSONAPLEX_LOWVRAM"))
        if detected_vram_gb is not None and detected_vram_gb < min_vram_gb:
            low_vram_mode = True

        selected_model = self.config.low_vram_model_id if low_vram_mode else self.config.model_id

        signature = (
            selected_model,
            self.config.device,
            self.config.torch_dtype,
            str(low_vram_mode),
            str(self.config.cpu_offload),
        )
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

            pipeline_kwargs: dict[str, Any] = {
                "task": "text-to-speech",
                "model": selected_model,
            }

            pipeline_device = -1
            if self.config.device == "auto":
                pipeline_device = 0 if torch.cuda.is_available() else -1
            elif self.config.device.startswith("cuda"):
                pipeline_device = 0

            if not low_vram_mode and detected_vram_gb is not None and detected_vram_gb < min_vram_gb:
                raise RuntimeError(
                    f"Detected {detected_vram_gb:.1f}GB VRAM, but PersonaPlex requires at least {min_vram_gb:.1f}GB."
                )

            dtype = "auto"
            if self.config.torch_dtype != "auto":
                try:
                    dtype = getattr(torch, self.config.torch_dtype)
                except Exception:
                    dtype = "auto"

            if low_vram_mode:
                runtime_ok, runtime_message = check_personaplex_runtime(low_vram=True)
                if not runtime_ok:
                    raise RuntimeError(
                        "Low-VRAM PersonaPlex is not supported by the active runtime "
                        f"({runtime_message}). Use VOICEDNA_PERSONAPLEX_DEVICE=cpu or Piper fallback."
                    )
                try:
                    importlib.import_module("bitsandbytes")
                    BitsAndBytesConfig = getattr(transformers, "BitsAndBytesConfig")
                except Exception as error:
                    raise RuntimeError(
                        "Low-VRAM PersonaPlex mode requires bitsandbytes. "
                        "Install with: pip install \"voicedna[personaplex-lowvram]\""
                    ) from error

                offload_dir = Path(
                    os.getenv(
                        "VOICEDNA_PERSONAPLEX_OFFLOAD_DIR",
                        str(Path.home() / ".cache" / "voicedna" / "personaplex-offload"),
                    )
                )
                offload_dir.mkdir(parents=True, exist_ok=True)

                quant_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_compute_dtype=getattr(torch, "float16", None),
                )

                model_kwargs: dict[str, Any] = {
                    "quantization_config": quant_config,
                    "device_map": "auto",
                    "low_cpu_mem_usage": True,
                }
                if self.config.cpu_offload:
                    model_kwargs.update({
                        "offload_state_dict": True,
                        "offload_folder": str(offload_dir),
                    })

                pipeline_kwargs["model_kwargs"] = model_kwargs
                pipeline_kwargs["device_map"] = "auto"
            else:
                pipeline_kwargs["device"] = pipeline_device
                pipeline_kwargs["torch_dtype"] = dtype

            try:
                PersonaPlexTTS._shared_pipeline = pipeline(**pipeline_kwargs)
                PersonaPlexTTS._shared_signature = signature
            except Exception as error:
                raise RuntimeError(
                    "Failed to initialize PersonaPlex TTS pipeline. "
                    "Verify model availability, transformers compatibility (4.x), and GPU/VRAM requirements for "
                    f"{selected_model}. "
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
