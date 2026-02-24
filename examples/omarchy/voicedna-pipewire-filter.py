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
from voicedna.providers import PersonaPlexTTS


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
    processor = VoiceDNAProcessor()
    provider = PersonaPlexTTS(
        model_id=os.getenv("VOICEDNA_PERSONAPLEX_MODEL", "nvidia/personaplex-7b-v1"),
        device=os.getenv("VOICEDNA_PERSONAPLEX_DEVICE", "auto"),
        torch_dtype=os.getenv("VOICEDNA_PERSONAPLEX_DTYPE", "auto"),
    )
    params = {
        "audio_format": "wav",
        "base_model": "personaplex",
        "force_age": force_age,
        "imprint_converter.mode": os.getenv("VOICEDNA_IMPRINT_MODE", "simple"),
    }
    return processor.synthesize_and_process(text=text, dna=dna, tts_provider=provider, params=params)


def main() -> int:
    parser = argparse.ArgumentParser(description="PipeWire audio shim that applies VoiceDNA processing")
    parser.add_argument("--infile", default="-", help="Input audio file path, or '-' for stdin")
    parser.add_argument("--outfile", default="-", help="Output audio file path, or '-' for stdout")
    parser.add_argument("--force-age", type=float, default=None, help="Override perceived voice age for testing")
    parser.add_argument(
        "--tts-backend",
        choices=["simple", "personaplex"],
        default=os.getenv("VOICEDNA_TTS_BACKEND", "simple"),
        help="Backend to use when synthesizing text input",
    )
    args = parser.parse_args()

    raw = sys.stdin.buffer.read() if args.infile == "-" else open(args.infile, "rb").read()

    if args.tts_backend == "personaplex":
        text = raw.decode("utf-8", errors="ignore").strip()
        if not text:
            text = "VoiceDNA natural voice output."
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
