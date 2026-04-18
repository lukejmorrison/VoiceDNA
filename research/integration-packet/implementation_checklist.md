# Implementation checklist — VoiceDNA → OpenClaw voice pipeline

## 1) Confirm branch and baseline
```bash
cd /home/namshub/dev/VoiceDNA
git status --short --branch
git rev-parse --short HEAD
git branch --list 'feature/voicedna-openclaw-per-agent-voices'
git rev-parse 69d8d0c^{commit}
git describe --tags --exact-match 69d8d0c^{commit}
```
Expected: branch exists, commit resolves, tag is `v3.1.1`.

## 2) Use the opt-in env vars
```bash
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```
Optional fallback map lives in `voicedna/openclaw_live_voice.py`.

## 3) Edit the live OpenClaw seam
Primary files to wire:
- `/home/namshub/dev/openclaw/skills/audio-responder-tts/audio_tts_reply.sh`
- `/home/namshub/dev/openclaw/tools/voicedna_adapter.py`

OpenClaw should call `render_agent_voice(...)` only when `VOICEDNA_OPENCLAW_PRESETS=1`; otherwise keep existing TTS behavior.

## 4) VoiceDNA-side files already in place
- `/home/namshub/dev/VoiceDNA/voicedna/openclaw_adapter.py`
- `/home/namshub/dev/VoiceDNA/voicedna/openclaw_live_voice.py`
- `/home/namshub/dev/VoiceDNA/examples/openclaw_voicedemo.py`
- `/home/namshub/dev/VoiceDNA/tests/test_voice_adapter.py`
- `/home/namshub/dev/VoiceDNA/tests/test_openclaw_live_voice.py`

## 5) Local test commands
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -v
python -m pytest tests/test_openclaw_live_voice.py -v
python -m pytest
ruff check voicedna/openclaw_adapter.py voicedna/openclaw_live_voice.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py tests/test_openclaw_live_voice.py
python -m py_compile voicedna/openclaw_adapter.py voicedna/openclaw_live_voice.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py tests/test_openclaw_live_voice.py
```

## 6) Demo generation
```bash
cd /home/namshub/dev/VoiceDNA
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
```
Expected outputs:
- `examples/openclaw/output/namshub_neutral.wav`
- `examples/openclaw/output/david_friendly.wav`
- `examples/openclaw/output/voss_flair.wav`

## 7) Validate demo WAVs
```bash
cd /home/namshub/dev/VoiceDNA
python - <<'PY'
from pathlib import Path
import wave
for path in sorted(Path('examples/openclaw/output').glob('*.wav')):
    with wave.open(str(path), 'rb') as w:
        print(path, 'channels=', w.getnchannels(), 'rate=', w.getframerate(), 'frames=', w.getnframes())
PY
```
Also verify each file is non-empty:
```bash
stat -c '%n %s bytes' examples/openclaw/output/*.wav
```

## 8) CI expectations
- VoiceDNA CI should continue to run `pytest -q` and compile checks.
- The live integration test should be allowed to skip cleanly if runtime backend deps are missing.
- No GitHub Actions workflow changes are needed for this pilot.

## 9) Demo/rollout checks before merge
- Confirm preset selection:
  - `agent:namshub` → `neutral`
  - `agent:david-hardman` → `friendly`
  - `agent:dr-voss-thorne` → `flair`
- Confirm fallback behavior remains unchanged when the env flag is absent.
- Confirm no unintended files are staged.
