from __future__ import annotations

import os
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
    ):
        self.model_path = model_path or os.getenv("VOICEDNA_PIPER_MODEL", "")
        self.executable = executable
        self.speaker_id = speaker_id or os.getenv("VOICEDNA_PIPER_SPEAKER", "")

        if not self.model_path:
            raise RuntimeError(
                "Piper backend requires a model path. Set VOICEDNA_PIPER_MODEL to a valid .onnx model file."
            )

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