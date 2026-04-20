#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/namshub/dev/VoiceDNA"
OUT_DIR="$ROOT/research/demo_output"
WAV="$OUT_DIR/demo.wav"

mkdir -p "$OUT_DIR"

bash "$ROOT/research/demo_commands.sh"

python - <<'PY'
from pathlib import Path
import sys
import wave

wav_path = Path('/home/namshub/dev/VoiceDNA/research/demo_output/demo.wav')
if not wav_path.exists():
    print(f'FAIL: missing output file: {wav_path}', file=sys.stderr)
    raise SystemExit(1)

raw = wav_path.read_bytes()
if len(raw) < 44:
    print(f'FAIL: file too small to be a WAV: {wav_path}', file=sys.stderr)
    raise SystemExit(1)
if raw[:4] != b'RIFF' or raw[8:12] != b'WAVE':
    print('FAIL: missing RIFF/WAVE header', file=sys.stderr)
    raise SystemExit(1)

with wave.open(str(wav_path), 'rb') as wav_file:
    channels = wav_file.getnchannels()
    sample_rate = wav_file.getframerate()
    sampwidth = wav_file.getsampwidth()
    frames = wav_file.getnframes()

if channels != 1 or sample_rate != 22050 or sampwidth != 2 or frames <= 0:
    print(
        f'FAIL: unexpected WAV format: channels={channels}, rate={sample_rate}, width={sampwidth}, frames={frames}',
        file=sys.stderr,
    )
    raise SystemExit(1)

print(f'PASS: {wav_path} is a valid 22050 Hz, 16-bit mono WAV with {frames} frames')
PY
