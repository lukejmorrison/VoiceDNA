# VoiceDNA → OpenClaw Implementation Checklist

## 0) Quick verification
Confirm both repos and branches before making changes:
```bash
cd /home/namshub/dev/VoiceDNA && git status --short --branch && git branch --show-current
cd /home/namshub/openclaw && git status --short --branch && git branch --show-current
```

Expected current state observed in this workspace:
- VoiceDNA: `feature/voicedna-openclaw-per-agent-voices`
- OpenClaw: `feature/voicedna-openclaw-wiring`

## 1) Confirm the VoiceDNA integration files
These files already exist and should be the implementation reference:
- `voicedna/openclaw_adapter.py`
- `voicedna/openclaw_live_voice.py`
- `examples/openclaw_voicedemo.py`
- `tests/test_voice_adapter.py`
- `tests/test_openclaw_live_voice.py`

## 2) Use this exact opt-in config
```bash
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

Resolution order:
1. exact `agent_id`
2. `agent_name` alias
3. default preset (`neutral`)

## 3) Smoke-test the adapter locally
From the VoiceDNA repo root:
```bash
cd /home/namshub/dev/VoiceDNA
python examples/openclaw_voicedemo.py
```

Expected output files:
- `examples/openclaw/output/namshub_neutral.wav`
- `examples/openclaw/output/david_friendly.wav`
- `examples/openclaw/output/voss_flair.wav`

## 4) Run the local tests
From the VoiceDNA repo root:
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -q
python -m pytest tests/test_openclaw_live_voice.py -q
```

If synthesis dependencies are missing, keep the unit tests and allow the synthesis tests to skip cleanly.

## 5) Validate the generated WAVs
```bash
file /home/namshub/dev/VoiceDNA/examples/openclaw/output/*.wav
python - <<'PY'
from pathlib import Path
import wave
root = Path('/home/namshub/dev/VoiceDNA/examples/openclaw/output')
for p in sorted(root.glob('*.wav')):
    with wave.open(str(p), 'rb') as w:
        print(p.name, w.getnchannels(), w.getframerate(), w.getsampwidth(), w.getnframes())
PY
```

## 6) Handoff rules for engineering
- Keep the feature additive and opt-in.
- Do not change default VoiceDNA semantics.
- Wire OpenClaw only at the TTS boundary.
- Do not assume cloud APIs, secrets, or encrypted assets are available.

## 7) License / CI / push notes
- VoiceDNA is MIT licensed; no blocker was identified for the current pilot.
- No PAT is required unless a later diff touches `.github/workflows/*` or a token-based push is explicitly needed.
- If a push is needed, use:
```bash
cd /home/namshub/dev/VoiceDNA
git add research/voicedna_integration_summary.md research/implementation_checklist.md research/integration_packet.md
git commit -m "docs: finalize VoiceDNA OpenClaw integration packet"
git push -u origin feature/voicedna-openclaw-per-agent-voices
```

## 8) Precise next steps for Dr Voss
1. Keep `VOICEDNA_OPENCLAW_PRESETS` behind a feature flag.
2. Preserve `neutral`, `friendly`, `flair` as the only pilot presets.
3. Verify the fallback chain before wiring any OpenClaw live hook.
4. Add CI skips for synthesis-only tests if the backend is absent.
