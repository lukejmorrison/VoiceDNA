# feat: per-agent voice pilot — VoiceAdapter + OpenClaw demo (3 presets)

## Summary
This PR delivers the VoiceDNA per-agent voice pilot described in `research/voicedna_integration_summary.md` and tracked in `research/implementation_checklist.md`.
It adds an opt-in `VoiceAdapter` layer so OpenClaw agents can speak with distinct VoiceDNA presets, plus a runnable demo and unit/smoke coverage.

## Motivation
- Enable per-agent voice routing without changing existing VoiceDNA CLI/SDK defaults.
- Prove the pilot with local-first demo output and repeatable tests.
- Keep the integration additive and low-risk for the core API.

## What changed
- Added a `VoiceAdapter` API with deterministic preset selection and synthesis.
- Added pilot presets: `neutral`, `friendly`, and `flair`.
- Added per-agent mapping support with env-driven opt-in configuration.
- Added `examples/openclaw_voicedemo.py` to demonstrate three agents using distinct presets.
- Added unit tests for preset selection, fallback behavior, env loading, and synthesis smoke coverage.
- Kept the feature opt-in so current public behavior stays unchanged unless configured.

## Validation
- `python -m pytest tests/test_voice_adapter.py -v`
- `python -m pytest`
- `python examples/openclaw_voicedemo.py`
- `ruff` linting
- `mypy` on the new adapter file

## Demo outputs
Expected demo WAVs:
- `examples/openclaw/output/namshub_neutral.wav`
- `examples/openclaw/output/david_friendly.wav`
- `examples/openclaw/output/voss_flair.wav`

## Rollout / rollback
### Rollout
- Merge behind the opt-in config path only.
- Validate the demo and adapter in one pilot environment before broader use.
- Keep current default presets and API surface unchanged.

### Rollback
- Disable the opt-in mapping/config to revert to existing behavior.
- Remove or ignore the demo path if the pilot needs to be paused.
- Revert this PR if any regression appears in core VoiceDNA behavior.

## References
- `research/voicedna_integration_summary.md`
- `research/implementation_checklist.md`

## Files touched
- `voicedna/openclaw_adapter.py`
- `examples/openclaw_voicedemo.py`
- `tests/test_voice_adapter.py`
- `README.md`
- `CHANGELOG.md`
- `IMPLEMENTATION_NOTE.md`
