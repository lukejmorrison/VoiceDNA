#!/usr/bin/env python3
"""User-level daemon for keeping VoiceDNA desktop runtime active on Omarchy.

Behavior:
- Loads encrypted VoiceDNA at startup and periodically (health checks)
- Password resolution: env VOICEDNA_PASSWORD, then optional keyring lookup
- Optional startup announcement via spd-say
"""

from __future__ import annotations

import logging
import os
import subprocess
import time
from pathlib import Path

from voice_dna import VoiceDNA


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


def main() -> int:
    interval = int(os.getenv("VOICEDNA_DAEMON_INTERVAL_SECONDS", "120"))
    _announce_once()

    while True:
        try:
            dna = _load_dna()
            logger.info(
                "VoiceDNA daemon alive | fingerprint=%s | age=%.2f",
                dna.get_recognition_id(),
                dna.get_current_age(),
            )
        except Exception as error:
            logger.error("VoiceDNA daemon health check failed: %s", error)

        time.sleep(max(15, interval))


if __name__ == "__main__":
    raise SystemExit(main())
