# VoiceDNA ↔ OpenClaw integration packet

Hand-off for Dr Voss. Keep this local-first, opt-in, and additive.

## Sources consolidated
- `research/voicedna_integration_summary.md`
- `research/implementation_checklist.md`
- `research/voicedna_integration_design.md`
- `research/integration-prep.md`
- current test/demo files in the repo

## What already exists
These files are already present and form the pilot implementation reference:
- `voicedna/openclaw_adapter.py`
- `voicedna/openclaw_live_voice.py`
- `examples/openclaw_voicedemo.py`
- `tests/test_voice_adapter.py`
- `tests/test_openclaw_live_voice.py`

## Core behavior to preserve
- Default VoiceDNA behavior must remain unchanged.
- OpenClaw should only route through VoiceDNA when `VOICEDNA_OPENCLAW_PRESETS=1` is set.
- Preset resolution order must stay:
  1. `agent_id`
  2. `agent_name` alias
  3. default preset (`neutral`)
- Only three pilot presets are in scope: `neutral`, `friendly`, `flair`.

## Canonical pilot mapping
```json
{
  "agent:namshub": "neutral",
  "agent:david-hardman": "friendly",
  "agent:dr-voss-thorne": "flair"
}
```

### Env form
```bash
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

## Exact integration notes
Wire VoiceDNA only at the OpenClaw TTS boundary:
- call the live-voice bridge first
- if the opt-in flag is absent, return `None` and let the existing OpenClaw path continue
- keep the adapter lazy-loaded
- do not change default TTS behavior for non-VoiceDNA users
- preserve the fallback chain and feature-flag semantics

## Local commands
### Install / test
```bash
cd /home/namshub/dev/VoiceDNA
python -m pip install -e ".[dev]"
python -m pytest tests/test_voice_adapter.py -q
python -m pytest tests/test_openclaw_live_voice.py -q
```

### Smoke test / demo artifact generation
```bash
cd /home/namshub/dev/VoiceDNA
bash research/smoke_test_tts.sh
```

### Demo / artifact generation
```bash
cd /home/namshub/dev/VoiceDNA
VOICEDNA_OPENCLAW_PRESETS=1 \
VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}' \
PYTHONPATH=. \
python examples/openclaw_voicedemo.py
```

### Validate WAV output
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

## CI plan
Recommended CI steps:
```bash
python -m pip install -e ".[dev]"
python -m pytest tests/test_voice_adapter.py tests/test_openclaw_live_voice.py -q
```
If the synthesis backend is unavailable, keep those tests skippable and avoid turning backend absence into a hard CI failure.

## Missing notes / guardrails
- Do not add cloud API dependencies for the pilot.
- Do not paste secrets into docs, code, or memory.
- Keep any future licensed assets or sample packs out of the repo unless redistribution rights are explicit.
- No PAT is required unless a later change touches GitHub workflows or token-based publishing is requested.

## Blockers requiring human approval
BLOCKER: GitHub PAT/token is needed only if Dr Voss must push or open a PR from a machine without existing Git auth.
- Requested scopes: `contents:write`, `pull_requests:write`
- Add `workflow` only if future work touches `.github/workflows/*`

BLOCKER: Any future licensed asset pack or encrypted voice asset would need explicit redistribution approval before being committed.

BLOCKER: A future preset expansion beyond `neutral`, `friendly`, and `flair` may require a license/provenance review before shipping.

## Suggested implementer checklist
1. Confirm `VOICEDNA_OPENCLAW_PRESETS` remains the only enable switch.
2. Keep `neutral`, `friendly`, `flair` as the only pilot presets.
3. Preserve `agent_id -> agent_name -> default` resolution.
4. Wire only the TTS boundary; leave the rest of OpenClaw unchanged.
5. Run the adapter and live-voice tests locally.
6. Run the demo and validate WAV files.
7. Stop and request approval before any push that needs new credentials.
