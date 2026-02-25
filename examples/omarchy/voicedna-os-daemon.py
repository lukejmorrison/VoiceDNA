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
from voicedna.synthesis import detect_natural_backend_decision, select_natural_backend, synthesize_and_process


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
    return os.getenv("VOICEDNA_TTS_BACKEND", "auto")


def _resolve_lowvram(cli_lowvram: bool) -> bool:
    if cli_lowvram:
        return True
    return os.getenv("VOICEDNA_PERSONAPLEX_LOWVRAM", "0").strip().lower() in {"1", "true", "yes", "on"}


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


def _synthesize_natural_test_phrase(dna: VoiceDNA, backend: str, low_vram: bool) -> tuple[bytes, dict]:
    audio, report, _ = synthesize_and_process(
        text="VoiceDNA natural desktop voice is active on your Omarchy system.",
        dna=dna,
        backend=backend,
        natural_voice=(backend == "auto"),
        low_vram=low_vram,
    )
    return audio, report


def _announce_backend(backend: str, dna: VoiceDNA, low_vram: bool) -> None:
    if os.getenv("VOICEDNA_DAEMON_ANNOUNCE", "0") != "1":
        return

    if backend == "simple":
        _announce_once()
        return

    try:
        audio, report = _synthesize_natural_test_phrase(dna, backend=backend, low_vram=low_vram)
        status = report.get("natural_backend_status")
        if status:
            logger.info("%s", status)
        _play_wav_bytes(audio)
    except Exception as error:
        logger.warning("Natural backend announce failed, falling back to spd-say: %s", error)
        _announce_once()


def main() -> int:
    parser = argparse.ArgumentParser(description="VoiceDNA Omarchy daemon")
    parser.add_argument(
        "--tts-backend",
        choices=["auto", "simple", "personaplex", "piper"],
        default=None,
        help="TTS backend used for daemon announce/probe path",
    )
    parser.add_argument(
        "--lowvram",
        action="store_true",
        help="Force low-VRAM PersonaPlex mode (4-bit + CPU offload)",
    )
    args = parser.parse_args()

    backend = _resolve_tts_backend(args.tts_backend)
    low_vram = _resolve_lowvram(args.lowvram)
    interval = int(os.getenv("VOICEDNA_DAEMON_INTERVAL_SECONDS", "120"))
    if backend == "auto":
        selected_backend, natural_status = select_natural_backend(force_low_vram=low_vram)
        decision = detect_natural_backend_decision(force_low_vram=low_vram)
        logger.info("VoiceDNA daemon backend selected: auto -> %s", selected_backend)
        logger.info("%s", natural_status)
        logger.info(
            "BACKEND STARTUP: backend=%s vram=%sGB required=%sGB lowvram=%s",
            decision.backend,
            f"{decision.detected_vram_gb:.1f}" if decision.detected_vram_gb is not None else "N/A",
            f"{decision.required_vram_gb:.1f}",
            str(decision.low_vram_mode).lower(),
        )
    else:
        selected_backend = backend
        logger.info("VoiceDNA daemon backend selected: %s", selected_backend)
        logger.info(
            "BACKEND STARTUP: backend=%s (manual override) lowvram=%s",
            selected_backend,
            str(low_vram).lower(),
        )

    if selected_backend in {"personaplex", "piper"}:
        try:
            dna = _load_dna()
            _announce_backend(selected_backend, dna, low_vram=low_vram)
        except Exception as error:
            logger.warning("Natural backend startup probe failed; continuing with simple fallback: %s", error)
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
            if selected_backend in {"personaplex", "piper"}:
                logger.info("Natural voice backend ready: %s", selected_backend)
        except Exception as error:
            logger.error("VoiceDNA daemon health check failed: %s", error)

        time.sleep(max(15, interval))


if __name__ == "__main__":
    raise SystemExit(main())
