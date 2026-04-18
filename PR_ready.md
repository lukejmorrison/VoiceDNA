# PR Ready — VoiceDNA per-agent voice pilot

## 3-item TODO
1. Confirm the `POST /api/auth/token` contract and permission model, then freeze the PR body.
2. Decide whether persistent download JSONL is in-scope for this pilot or should stay as a follow-up.
3. Schedule the founder interview to validate the first sellable product shape before expanding the surface area.

## PR title
**feat: per-agent voice pilot — VoiceAdapter + OpenClaw demo (3 presets)**

## PR description
This PR adds an opt-in OpenClaw adapter that maps agent identity to stable VoiceDNA presets, so Namshub, Dr Voss Thorne, and David Hardman can each speak with distinct voices without changing the default VoiceDNA behavior.

### What it changes
- Adds `voicedna/openclaw_adapter.py` with deterministic preset routing:
  `agent_id` → `agent_name` → default preset.
- Ships three pilot presets only: `neutral`, `friendly`, `flair`.
- Adds `examples/openclaw_voicedemo.py` to generate local WAV output for the pilot.
- Adds focused coverage in `tests/test_voice_adapter.py`.
- Updates docs and rollout notes so the feature stays opt-in and easy to back out.

### Why it is low risk
- No default behavior changes.
- No cloud dependency for the demo path.
- The adapter is isolated and can be disabled without affecting the rest of VoiceDNA.

## Release notes
- New opt-in per-agent voice routing for OpenClaw personas.
- Three preset pilot only: `neutral`, `friendly`, `flair`.
- Local demo script included for review and sanity checks.
- Backwards compatible: existing VoiceDNA defaults remain unchanged.
- Rollback is simple: disable the adapter or remove the pilot wiring.

## Test checklist
- [x] `python -m pytest tests/test_voice_adapter.py tests/test_consistency_engine.py` — **17 passed, 3 skipped**
- [ ] `python -m pytest` in a dependency-complete environment
- [ ] `python examples/openclaw_voicedemo.py` where the VoiceDNA runtime backend is available
- [ ] Confirm no unintended files are included in the PR
- [ ] Verify reviewer sign-off from Namshub / Dr Voss Thorne

## Push options
See `/home/namshub/notes/voice_pr_push_options.md` for the two safe push paths:
- Option A: short-lived PAT + direct Git push / PR creation
- Option B: local git bundle handoff for a trusted-machine push

## Reviewer notes
- Keep the PR scoped to the additive pilot.
- Do not expand to workflow changes unless explicitly planned.
- If `POST /api/auth/token` or persistent JSONL logging becomes part of the pilot, capture that in a follow-up decision before merge.
