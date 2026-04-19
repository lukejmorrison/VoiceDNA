# VoiceDNA → OpenClaw VoiceAdapter Design Doc

## Goal
Add an opt-in, backwards-compatible per-agent voice routing layer so OpenClaw agents can speak with distinct VoiceDNA presets without changing existing VoiceDNA defaults.

## Current state
- Adapter exists: `voicedna/openclaw_adapter.py`
- Demo exists: `examples/openclaw_voicedemo.py`
- Demo WAVs exist under: `examples/openclaw/output/`
- Presets in scope: `neutral`, `friendly`, `flair`

## Approach
1. Resolve a preset for each agent using deterministic precedence:
   - `agent_id`
   - `agent_name` alias
   - default preset (`neutral`)
2. Keep the path opt-in via environment variables or direct adapter construction.
3. Synthesize locally and emit WAV bytes; optionally write to a file.
4. Preserve existing VoiceDNA CLI/SDK behavior unless the adapter is explicitly used.

## Environment variables
- `VOICEDNA_OPENCLAW_PRESETS=1`
  - opt-in flag for the pilot path
- `VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'`
  - optional JSON mapping of agent IDs or aliases to presets

## Deployment / rollout steps
1. Merge the adapter and demo behind the opt-in flag.
2. Keep the mapping small and explicit for the pilot.
3. Validate demo WAV generation locally.
4. If later wired into OpenClaw, keep the adapter boundary stable so the core voice pipeline can swap implementations without changing agent semantics.

## Implementation commands
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -v
python -m pytest tests/test_openclaw_live_voice.py -v
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
```

## Validation commands
```bash
file examples/openclaw/output/*.wav
python - <<'PY'
from pathlib import Path
for p in Path('examples/openclaw/output').glob('*.wav'):
    print(p.name, p.stat().st_size)
PY
```

## Notes
- This is intentionally local-first: no cloud dependency is required for the pilot path.
- If runtime dependencies are missing in the current environment, install the project requirements before running the demo or full suite.
