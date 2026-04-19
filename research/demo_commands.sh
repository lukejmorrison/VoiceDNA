#!/usr/bin/env bash
set -euo pipefail

# VoiceDNA → OpenClaw per-agent voice pilot smoke/demo commands.
# Run from anywhere; each command enters the VoiceDNA repo explicitly.

cd /home/namshub/dev/VoiceDNA

# 1) Optional editable install if you are setting up a fresh local env
python -m pip install -e ".[dev]"

# 2) Run the adapter and live-voice tests
python -m pytest tests/test_voice_adapter.py -q
python -m pytest tests/test_openclaw_live_voice.py -q

# 3) Run the full VoiceDNA test suite
python -m pytest -q

# 4) Generate the three demo WAVs
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py

# 5) Confirm the generated files are present
ls -lh examples/openclaw/output/*.wav

# 6) Confirm each WAV is RIFF/WAVE and inspect the format
file examples/openclaw/output/*.wav
python - <<'PY'
from pathlib import Path
import wave
root = Path('/home/namshub/dev/VoiceDNA/examples/openclaw/output')
for p in sorted(root.glob('*.wav')):
    with wave.open(str(p), 'rb') as w:
        print(p.name, 'channels=', w.getnchannels(), 'rate=', w.getframerate(), 'width=', w.getsampwidth(), 'frames=', w.getnframes())
PY
