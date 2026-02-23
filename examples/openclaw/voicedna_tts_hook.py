"""OpenClaw skill-style VoiceDNA TTS hook.

This module is designed to be copy/pasted into an OpenClaw skills or extensions folder.
It loads `myai.voicedna.enc`, wraps any raw TTS bytes, runs VoiceDNA processing,
and returns processed audio bytes.
"""

from __future__ import annotations

import getpass
import json
import logging
import os
from pathlib import Path
from typing import Any, Callable

from voice_dna import VoiceDNA
from voicedna import VoiceDNAProcessor


logger = logging.getLogger("voicedna.openclaw")


class VoiceDNATTSHook:
    def __init__(self, encrypted_path: str = "myai.voicedna.enc", password: str | None = None):
        self.encrypted_path = encrypted_path
        self.password = password
        self.dna = self._load_dna()
        self.processor = VoiceDNAProcessor()

    def _resolve_password(self) -> str:
        if self.password:
            return self.password

        env_password = os.getenv("VOICEDNA_PASSWORD")
        if env_password:
            return env_password

        return getpass.getpass("VoiceDNA password for myai.voicedna.enc: ")

    def _load_dna(self) -> VoiceDNA:
        password = self._resolve_password()
        path = os.getenv("VOICEDNA_ENC_PATH", self.encrypted_path)
        resolved = Path(path)
        if not resolved.exists():
            raise FileNotFoundError(
                f"VoiceDNA encrypted file not found at '{resolved}'. "
                "Set VOICEDNA_ENC_PATH or place myai.voicedna.enc in the working directory."
            )
        return VoiceDNA.load_encrypted(password=password, filepath=str(resolved))

    def process_tts_output(self, raw_audio_bytes: bytes, text: str = "", base_model: str = "openclaw") -> bytes:
        force_age_env = os.getenv("VOICEDNA_FORCE_AGE")
        force_age = float(force_age_env) if force_age_env else None

        params: dict[str, Any] = {
            "text": text,
            "base_model": base_model,
            "force_age": force_age,
            "imprint_converter.mode": "rvc_stub",
            "imprint_converter.rvc_ready": True,
            "imprint_converter.rvc_note": "OpenClaw integration path: ready for downstream RVC conversion stage.",
        }

        processed = self.processor.process(raw_audio_bytes, self.dna, params)
        report = self.processor.get_last_report()

        logger.info("VoiceDNA age: %.2f", self.dna.get_current_age())
        logger.info("VoiceDNA report: %s", json.dumps(report, indent=2))
        return processed


# OpenClaw wiring option A (decorator style):
# from openclaw import skill
#
# @skill(name="voicedna_tts_hook")
# def voicedna_tts_hook_skill(text: str, raw_audio: bytes, provider: str = "openclaw") -> bytes:
#     return get_voicedna_tts_hook().process_tts_output(raw_audio, text=text, base_model=provider)


_cached_hook: VoiceDNATTSHook | None = None


def get_voicedna_tts_hook() -> VoiceDNATTSHook:
    global _cached_hook
    if _cached_hook is None:
        _cached_hook = VoiceDNATTSHook()
    return _cached_hook


# OpenClaw wiring option B (exported function style):
def process_tts_output(raw_audio_bytes: bytes, text: str = "", provider_name: str = "openclaw") -> bytes:
    return get_voicedna_tts_hook().process_tts_output(
        raw_audio_bytes,
        text=text,
        base_model=provider_name,
    )


def wrap_tts_provider(tts_render_fn: Callable[..., bytes]) -> Callable[..., bytes]:
    """Wrap any TTS provider function that returns raw audio bytes."""

    def _wrapped(*args: Any, **kwargs: Any) -> bytes:
        text = kwargs.get("text") or (args[0] if args else "")
        raw = tts_render_fn(*args, **kwargs)
        return process_tts_output(raw, text=str(text), provider_name="openclaw")

    return _wrapped


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fake_tts = b"RAW_TTS_AUDIO_BYTES"
    out = process_tts_output(fake_tts, text="hello from OpenClaw + VoiceDNA")
    print(f"Input bytes: {len(fake_tts)} | Output bytes: {len(out)}")
