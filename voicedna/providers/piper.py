from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def piper_natural_message() -> str:
    return "Piper natural voice"


class PiperTTS:
    def __init__(
        self,
        model_path: str | None = None,
        executable: str = "piper",
        speaker_id: str | None = None,
        length_scale: float | None = None,
        noise_scale: float | None = None,
        noise_w: float | None = None,
    ):
        self.model_path = model_path or os.getenv("VOICEDNA_PIPER_MODEL", "")
        self.executable = executable
        self.speaker_id = speaker_id or os.getenv("VOICEDNA_PIPER_SPEAKER", "")
        self.length_scale = (
            float(os.getenv("VOICEDNA_PIPER_LENGTH_SCALE", "0.92")) if length_scale is None else float(length_scale)
        )
        self.noise_scale = (
            float(os.getenv("VOICEDNA_PIPER_NOISE_SCALE", "0.60")) if noise_scale is None else float(noise_scale)
        )
        self.noise_w = float(os.getenv("VOICEDNA_PIPER_NOISE_W", "0.78")) if noise_w is None else float(noise_w)

        if not self.model_path:
            resolved = _discover_piper_model_path()
            if resolved is None:
                searched = ", ".join(str(path) for path in _candidate_model_dirs())
                raise RuntimeError(
                    "Piper backend requires a model path. Set VOICEDNA_PIPER_MODEL to a valid .onnx model file "
                    f"(searched: {searched})."
                )
            self.model_path = str(resolved)

        model = Path(self.model_path).expanduser()
        if not model.exists():
            raise RuntimeError(f"Piper model file not found: {model}")

        self.model_path = str(model)

    def synthesize(self, text: str, sample_rate: int = 22050) -> bytes:
        if not text or not text.strip():
            raise ValueError("Text for Piper synthesis must not be empty")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
            output_wav = Path(handle.name)

        command = [self.executable, "--model", self.model_path, "--output_file", str(output_wav)]
        if self.speaker_id:
            command.extend(["--speaker", self.speaker_id])
        command.extend([
            "--length_scale",
            f"{self.length_scale:.3f}",
            "--noise_scale",
            f"{self.noise_scale:.3f}",
            "--noise_w",
            f"{self.noise_w:.3f}",
        ])

        try:
            completed = subprocess.run(
                command,
                input=text,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                stderr = (completed.stderr or "").strip()
                raise RuntimeError(stderr or "piper synthesis failed")
            return output_wav.read_bytes()
        finally:
            output_wav.unlink(missing_ok=True)


def _candidate_model_dirs() -> list[Path]:
    configured_dir = os.getenv("VOICEDNA_PIPER_MODEL_DIR", "").strip()
    paths = [
        Path(configured_dir).expanduser() if configured_dir else None,
        Path.home() / ".local" / "share" / "piper",
        Path.home() / ".cache" / "piper",
        Path("/usr/share/piper"),
        Path("/opt/piper/models"),
    ]
    return [path for path in paths if path is not None]


def _discover_piper_model_path() -> Path | None:
    preferred_names = [
        "en_US-lessac-medium.onnx",
        "en_US-amy-medium.onnx",
        "en_US-ryan-medium.onnx",
        "en_US-lessac-low.onnx",
    ]

    for directory in _candidate_model_dirs():
        if not directory.exists():
            continue
        for file_name in preferred_names:
            candidate = directory / file_name
            if candidate.exists():
                return candidate

    for directory in _candidate_model_dirs():
        if not directory.exists():
            continue
        matches = sorted(directory.rglob("*.onnx"))
        if matches:
            return matches[0]

    return None


def check_piper_runtime(model_path: str | None = None) -> tuple[bool, str, str | None]:
    executable = os.getenv("VOICEDNA_PIPER_EXECUTABLE", "piper")
    if shutil.which(executable) is None:
        return False, "Piper executable not found in PATH", None

    candidate_path = (model_path or os.getenv("VOICEDNA_PIPER_MODEL", "")).strip()
    resolved_model: Path | None
    if candidate_path:
        resolved_model = Path(candidate_path).expanduser()
    else:
        resolved_model = _discover_piper_model_path()

    if resolved_model is None or not resolved_model.exists():
        return (
            False,
            "No Piper model found. Set VOICEDNA_PIPER_MODEL to a local .onnx file for best 8GB fallback quality.",
            None,
        )

    return True, f"Piper ready with model: {resolved_model}", str(resolved_model)