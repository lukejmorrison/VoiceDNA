#!/usr/bin/env python3
"""VoiceDNA PipeWire filter shim for Omarchy desktop speech.

Example usage:
  cat raw_tts_audio.bin | ./voicedna-pipewire-filter.py > processed_audio.bin

A real PipeWire filter-chain can invoke this script as a process node wrapper.
"""

from __future__ import annotations

import argparse
import getpass
import os
import sys

from voice_dna import VoiceDNA
from voicedna import VoiceDNAProcessor
from voicedna.synthesis import synthesize_and_process


def load_dna() -> VoiceDNA:
    path = os.getenv("VOICEDNA_ENC_PATH", "myai.voicedna.enc")
    password = os.getenv("VOICEDNA_PASSWORD") or getpass.getpass("VoiceDNA password: ")
    return VoiceDNA.load_encrypted(password=password, filepath=path)


def process_bytes(audio_bytes: bytes, force_age: float | None) -> bytes:
    dna = load_dna()
    processor = VoiceDNAProcessor()
    params = {
        "base_model": "omarchy_pipewire",
        "force_age": force_age,
        "imprint_converter.mode": "rvc_stub",
        "imprint_converter.rvc_ready": True,
        "imprint_converter.rvc_note": "Omarchy PipeWire shim path.",
    }
    return processor.process(audio_bytes, dna, params)


def synthesize_text(text: str, force_age: float | None) -> bytes:
    dna = load_dna()
    params = {
        "force_age": force_age,
        "imprint_converter.mode": os.getenv("VOICEDNA_IMPRINT_MODE", "simple"),
    }
    audio, _, _ = synthesize_and_process(
        text=text,
        dna=dna,
        backend=os.getenv("VOICEDNA_TTS_BACKEND", "auto"),
        natural_voice=True,
        params=params,
    )
    return audio


def main() -> int:
    parser = argparse.ArgumentParser(description="PipeWire audio shim that applies VoiceDNA processing")
    parser.add_argument("--infile", default="-", help="Input audio file path, or '-' for stdin")
    parser.add_argument("--outfile", default="-", help="Output audio file path, or '-' for stdout")
    parser.add_argument("--force-age", type=float, default=None, help="Override perceived voice age for testing")
    parser.add_argument(
        "--tts-backend",
        choices=["auto", "simple", "personaplex", "piper"],
        default=os.getenv("VOICEDNA_TTS_BACKEND", "auto"),
        help="Backend to use when synthesizing text input",
    )
    args = parser.parse_args()

    raw = sys.stdin.buffer.read() if args.infile == "-" else open(args.infile, "rb").read()

    if args.tts_backend in {"auto", "personaplex", "piper"}:
        text = raw.decode("utf-8", errors="ignore").strip()
        if not text:
            text = "VoiceDNA natural voice output."
        os.environ["VOICEDNA_TTS_BACKEND"] = args.tts_backend
        processed = synthesize_text(text, force_age=args.force_age)
    else:
        processed = process_bytes(raw, force_age=args.force_age)

    if args.outfile == "-":
        sys.stdout.buffer.write(processed)
    else:
        with open(args.outfile, "wb") as output_handle:
            output_handle.write(processed)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
