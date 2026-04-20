#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/namshub/dev/VoiceDNA"
OUT_DIR="$ROOT/research/demo_output"
OUT_WAV="$OUT_DIR/demo.wav"

mkdir -p "$OUT_DIR"

python - <<'PY'
from pathlib import Path
import math
import struct
import wave

root = Path('/home/namshub/dev/VoiceDNA')
out_dir = root / 'research' / 'demo_output'
out_wav = out_dir / 'demo.wav'

sample_rate = 22050
bit_depth_bytes = 2
channels = 1
seconds = 0.25
frames = int(sample_rate * seconds)

with wave.open(str(out_wav), 'wb') as wav_file:
    wav_file.setnchannels(channels)
    wav_file.setsampwidth(bit_depth_bytes)
    wav_file.setframerate(sample_rate)
    for i in range(frames):
        sample = int(32767 * 0.2 * math.sin(2 * math.pi * 440 * i / sample_rate))
        wav_file.writeframesraw(struct.pack('<h', sample))

print(out_wav)
PY

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

expected_sample_rate = 22050
expected_sampwidth = 2
if channels != 1:
    print(f'FAIL: expected mono WAV, got {channels} channels', file=sys.stderr)
    raise SystemExit(1)
if sample_rate != expected_sample_rate:
    print(f'FAIL: expected sample rate {expected_sample_rate}, got {sample_rate}', file=sys.stderr)
    raise SystemExit(1)
if sampwidth != expected_sampwidth:
    print(f'FAIL: expected {expected_sampwidth * 8}-bit PCM, got {sampwidth * 8}-bit', file=sys.stderr)
    raise SystemExit(1)
if frames <= 0:
    print('FAIL: expected at least one audio frame', file=sys.stderr)
    raise SystemExit(1)

print(f'PASS: {wav_path} is a valid {sample_rate} Hz, {sampwidth * 8}-bit mono WAV with {frames} frames')
PY
