#!/usr/bin/env python3
"""User-level daemon for keeping VoiceDNA desktop runtime active on Omarchy.

Behavior:
- Loads encrypted VoiceDNA at startup and periodically (health checks)
- Password resolution: env VOICEDNA_PASSWORD, then optional keyring lookup
- Optional startup announcement via spd-say
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import time
from pathlib import Path

from voice_dna import VoiceDNA
from voicedna import VoiceDNAProcessor
from voicedna.providers import PersonaPlexTTS


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("voicedna.os.daemon")


def _get_password() -> str | None:
    env_password = os.getenv("VOICEDNA_PASSWORD")
    if env_password:
        return env_password

    try:
        import keyring  # type: ignore

        return keyring.get_password("voicedna", "default")
    except Exception:
        return None


def _get_dna_path() -> Path:
    return Path(os.getenv("VOICEDNA_ENC_PATH", str(Path.home() / "myai.voicedna.enc"))).expanduser()


def _load_dna() -> VoiceDNA:
    dna_path = _get_dna_path()
    if not dna_path.exists():
        raise FileNotFoundError(f"Encrypted VoiceDNA file not found: {dna_path}")

    password = _get_password()
    if not password:
        raise RuntimeError(
            "No VoiceDNA password configured. Set VOICEDNA_PASSWORD in ~/.config/voicedna/daemon.env "
            "or store keyring secret for service=voicedna user=default."
        )

    return VoiceDNA.load_encrypted(password=password, filepath=str(dna_path))


def _announce_once() -> None:
    if os.getenv("VOICEDNA_DAEMON_ANNOUNCE", "0") != "1":
        return
    try:
        subprocess.run(
            ["spd-say", "VoiceDNA desktop daemon is active."],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def _resolve_tts_backend(cli_backend: str | None) -> str:
    if cli_backend:
        return cli_backend
    return os.getenv("VOICEDNA_TTS_BACKEND", "simple")


def _play_wav_bytes(audio_bytes: bytes) -> None:
    with subprocess.Popen(
        ["pw-play", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ) as process:
        assert process.stdin is not None
        process.stdin.write(audio_bytes)
        process.stdin.close()
        process.wait(timeout=15)


def _synthesize_personaplex_test_phrase(dna: VoiceDNA) -> bytes:
    provider = PersonaPlexTTS(
        model_id=os.getenv("VOICEDNA_PERSONAPLEX_MODEL", "nvidia/personaplex-7b-v1"),
        device=os.getenv("VOICEDNA_PERSONAPLEX_DEVICE", "auto"),
        torch_dtype=os.getenv("VOICEDNA_PERSONAPLEX_DTYPE", "auto"),
    )
    processor = VoiceDNAProcessor()
    return processor.synthesize_and_process(
        "VoiceDNA PersonaPlex backend is active on your Omarchy desktop.",
        dna,
        provider,
        {
            "audio_format": "wav",
            "base_model": "personaplex",
            "imprint_converter.mode": os.getenv("VOICEDNA_IMPRINT_MODE", "simple"),
        },
    )


def _announce_backend(backend: str, dna: VoiceDNA) -> None:
    if os.getenv("VOICEDNA_DAEMON_ANNOUNCE", "0") != "1":
        return

    if backend != "personaplex":
        _announce_once()
        return

    try:
        audio = _synthesize_personaplex_test_phrase(dna)
        _play_wav_bytes(audio)
    except Exception as error:
        logger.warning("PersonaPlex announce failed, falling back to spd-say: %s", error)
        _announce_once()


def main() -> int:
    parser = argparse.ArgumentParser(description="VoiceDNA Omarchy daemon")
    parser.add_argument(
        "--tts-backend",
        choices=["simple", "personaplex"],
        default=None,
        help="TTS backend used for daemon announce/probe path",
    )
    args = parser.parse_args()

    backend = _resolve_tts_backend(args.tts_backend)
    interval = int(os.getenv("VOICEDNA_DAEMON_INTERVAL_SECONDS", "120"))
    logger.info("VoiceDNA daemon backend selected: %s", backend)

    if backend == "personaplex":
        try:
            dna = _load_dna()
            _announce_backend(backend, dna)
        except Exception as error:
            logger.warning("PersonaPlex startup probe failed; continuing with simple fallback: %s", error)
            _announce_once()
    else:
        _announce_once()

    while True:
        try:
            dna = _load_dna()
            logger.info(
                "VoiceDNA daemon alive | fingerprint=%s | age=%.2f",
                dna.get_recognition_id(),
                dna.get_current_age(),
            )
            if backend == "personaplex":
                logger.info("PersonaPlex natural voice backend ready")
        except Exception as error:
            logger.error("VoiceDNA daemon health check failed: %s", error)

        time.sleep(max(15, interval))


if __name__ == "__main__":
    raise SystemExit(main())
