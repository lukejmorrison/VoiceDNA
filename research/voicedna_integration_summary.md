# VoiceDNA → OpenClaw Per-Agent Voice Pilot Summary

Scope: VoiceDNA repo + OpenClaw example integration for per-agent voices.

## Verified files
Present and correct in the local VoiceDNA tree:
- `voicedna/openclaw_adapter.py`
- `voicedna/openclaw_live_voice.py`
- `examples/openclaw_voicedemo.py`
- `tests/test_voice_adapter.py`
- `tests/test_openclaw_live_voice.py`
- `research/implementation_checklist.md`

## What the integration does
- Adds an opt-in routing layer so OpenClaw agents can map to VoiceDNA presets.
- Uses a deterministic fallback order: `agent_id` → `agent_name` alias → default preset.
- Ships three pilot presets only: `neutral`, `friendly`, `flair`.
- Keeps default VoiceDNA behavior unchanged unless `VOICEDNA_OPENCLAW_PRESETS=1` is set.

## Current status
- The VoiceDNA source tree is present locally at `/home/namshub/dev/VoiceDNA`.
- The OpenClaw bridge is implemented as an additive, local-first path.
- The demo script writes WAVs under `examples/openclaw/output/`.
- License review found no blocker for the current pilot; VoiceDNA is MIT licensed.

## Implementation notes
1. `voicedna.openclaw_adapter.VoiceAdapter`
   - `select_preset(agent_id, agent_name=None)`
   - `synthesize(text, preset, output_path=None)`
   - optional runtime mapping from `VOICEDNA_OPENCLAW_PRESETS_MAP`

2. `voicedna.openclaw_live_voice.render_agent_voice(...)`
   - returns `None` when the opt-in env var is not set
   - preserves OpenClaw’s existing TTS path when disabled

3. `examples/openclaw_voicedemo.py`
   - demonstrates the three pilot agents
   - produces:
     - `namshub_neutral.wav`
     - `david_friendly.wav`
     - `voss_flair.wav`

## Config surface
Recommended env vars:
```bash
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

## CI / push notes
- No `.github/workflows/*` changes are required for this pilot.
- A PAT is **not required** for the current branch unless a later change touches workflows or token-based publishing is needed.
- If a push is needed, use the branch `feature/voicedna-openclaw-per-agent-voices`.

## Remaining gaps to keep in mind
- If future presets depend on external sample packs or licensed assets, document redistribution rights before shipping.
- Keep synthesis tests separate from unit tests so CI can skip them if the backend is unavailable.
