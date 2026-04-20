# VoiceDNA → OpenClaw Handoff Packet

## Status
- Summary doc present: `research/voicedna_integration_summary.md`
- Checklist present: `research/implementation_checklist.md`
- Demo WAVs present: `examples/openclaw/output/*.wav`
- Integration artifacts ready for implementation handoff.

## Checklist
- [x] Confirm adapter exists in `voicedna/openclaw_adapter.py`
- [x] Confirm demo exists in `examples/openclaw_voicedemo.py`
- [x] Confirm pilot presets: `neutral`, `friendly`, `flair`
- [x] Confirm demo outputs exist and are non-empty
- [x] Document env vars and local commands
- [x] Keep OpenClaw core unchanged in this repo

## Environment variables
```bash
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

## Exact local reproduction steps
```bash
cd /home/namshub/dev/VoiceDNA
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
PYTHONPATH=. python examples/openclaw_voicedemo.py
```

## Demo validation commands
```bash
file examples/openclaw/output/*.wav
python - <<'PY'
import wave
from pathlib import Path
for p in Path('examples/openclaw/output').glob('*.wav'):
    with wave.open(str(p), 'rb') as wf:
        print(p.name, wf.getnchannels(), wf.getframerate(), wf.getsampwidth(), wf.getnframes())
PY
```

## Test commands
```bash
python -m pytest tests/test_voice_adapter.py -v
python -m pytest tests/test_openclaw_live_voice.py -v
python -m pytest -q
```

## Known local blockers
- In this environment, repo-wide pytest has previously failed during collection when `cryptography` is missing.
- Demo synthesis can also fail if the VoiceDNA runtime backend packages are not installed.

## If you need to regenerate demo WAVs
```bash
rm -f examples/openclaw/output/*.wav
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
```

## Implementation note for Dr Voss
Keep any future OpenClaw wiring behind the same adapter boundary and the same opt-in flag so the pilot remains reversible.
