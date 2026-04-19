# VoiceDNA ↔ OpenClaw per-agent voice pilot

## Architecture summary
Add VoiceDNA as an **opt-in** voice-routing layer at the OpenClaw TTS boundary so agents can speak with distinct presets without changing default behavior. The routing order is deterministic:

1. `agent_id`
2. `agent_name` alias
3. default preset (`neutral`)

The pilot stays local-first and additive:
- no cloud dependency
- no schema migration
- no change to default VoiceDNA semantics unless the feature flag is enabled
- only three pilot presets: `neutral`, `friendly`, `flair`

## Required env vars
```bash
VOICEDNA_OPENCLAW_PRESETS=1
VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```
Optional / situational:
- `PYTHONPATH=.` if not using editable install
- any future secret vars only if encrypted/licensed assets are introduced later; none are required for the current pilot

## Exact changes at the OpenClaw TTS boundary
Wire the feature only where OpenClaw converts text to speech:
- call `voicedna.openclaw_live_voice.render_agent_voice(...)` before the existing TTS path
- if `VOICEDNA_OPENCLAW_PRESETS` is unset or falsey, return `None` and preserve the current OpenClaw TTS path
- if the flag is on, instantiate/use `VoiceAdapter` and resolve preset via `agent_id -> agent_name -> default`
- keep the bridge lazy-loaded and side-effect free until the env flag is enabled
- do not alter default output for non-VoiceDNA users

In practice, only the live voice hook should know about the adapter; the rest of OpenClaw should continue to treat TTS as a normal optional backend.

## Local test / CI plan
### Local
```bash
cd /home/namshub/dev/VoiceDNA
python -m pip install -e ".[dev]"
python -m pytest tests/test_voice_adapter.py -q
python -m pytest tests/test_openclaw_live_voice.py -q
python examples/openclaw_voicedemo.py
file examples/openclaw/output/*.wav
python - <<'PY'
from pathlib import Path
import wave
for p in sorted(Path('examples/openclaw/output').glob('*.wav')):
    with wave.open(str(p), 'rb') as w:
        print(p.name, w.getnchannels(), w.getframerate(), w.getsampwidth(), w.getnframes())
PY
```

### CI
Recommended CI job steps:
```bash
python -m pip install -e ".[dev]"
python -m pytest tests/test_voice_adapter.py tests/test_openclaw_live_voice.py -q
```
If the backend is unavailable in CI, keep synthesis tests skippable and do not fail the whole pipeline for missing local audio dependencies.

## Implementation checklist for Dr Voss
1. Confirm the feature remains behind `VOICEDNA_OPENCLAW_PRESETS=1`.
2. Keep only the three pilot presets in scope: `neutral`, `friendly`, `flair`.
3. Preserve the fallback chain exactly: `agent_id -> agent_name -> default`.
4. Wire the adapter only at the OpenClaw TTS boundary.
5. Keep the live-voice bridge returning `None` when disabled.
6. Verify the demo script still writes WAVs under `examples/openclaw/output/`.
7. Run the two pytest files locally.
8. Validate generated WAV headers and basic audio metadata.
9. If packaging/push is needed, confirm Git auth first; do not introduce PATs or workflow tokens unless explicitly approved.

## Rollback rule
If anything regresses, unset `VOICEDNA_OPENCLAW_PRESETS` and remove the TTS hook call site. The pilot is designed to be reversible with no data migration.
