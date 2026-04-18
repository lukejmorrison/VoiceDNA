# VoiceDNA per-agent voice pilot

## Purpose
Add opt-in per-agent voice routing for OpenClaw so individual agents can speak with distinct VoiceDNA presets without changing existing CLI or SDK defaults. The pilot keeps the feature local-first and additive: no cloud dependency, no default-behavior change, and no required migration for existing users.

## Design decisions
- Introduce `voicedna.openclaw_adapter.VoiceAdapter` as a small routing layer.
- Use deterministic preset selection: `agent_id` -> `agent_name` -> default preset.
- Ship three pilot presets only: `neutral`, `friendly`, `flair`.
- Keep activation opt-in via `VOICEDNA_OPENCLAW_PRESETS=1` / `VOICEDNA_OPENCLAW_PRESETS_MAP` or explicit construction.
- Provide a runnable local demo that writes WAV files to `examples/openclaw/output/`.
- Preserve existing VoiceDNA behavior unless the adapter is imported or the demo is run.

## Current implementation status
- Adapter code exists and is importable.
- Demo script exists and maps the three OpenClaw personas to the three presets.
- Unit tests cover preset selection, env loading, helper registration, and synthesis error paths.
- Existing demo WAV artifacts are present in the repo and non-empty.

## Migration / rollout plan
1. Merge the pilot behind the opt-in env flag and direct import path.
2. Keep README / implementation notes synchronized with the adapter API.
3. Optionally wire the adapter into OpenClaw integration points later, after the pilot is approved.
4. Expand preset mapping only after real-user validation.

## Rollback plan
- Remove the import/use of `VoiceAdapter` from OpenClaw wiring if it is added later.
- Disable the opt-in env flag path.
- Revert the adapter/demo/test files if the pilot needs to be backed out.
- Existing VoiceDNA core flows remain untouched, so rollback is low-risk.

## Estimated effort
- Pilot implementation: complete.
- PR polish and validation: small.
- Future OpenClaw integration wiring: low to moderate, depending on hook placement and runtime backend availability.
