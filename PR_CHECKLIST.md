# VoiceDNA per-agent voice pilot — PR Checklist

## Acceptance criteria
- [ ] Sample demo WAVs are included or can be generated locally by the demo script.
- [ ] Each agent maps to the intended preset and loads per-agent routing correctly.
- [ ] The adapter resolves presets deterministically: `agent_id` > `agent_name` > default.
- [ ] `neutral`, `friendly`, and `flair` presets exist and are valid.
- [ ] Synthesis produces bytes or writes a non-empty audio file for each preset.
- [ ] Unknown presets are rejected or skipped safely, with clear failure behavior.
- [ ] Existing VoiceDNA core API behavior remains unchanged unless opt-in config is enabled.
- [ ] The OpenClaw demo runs locally without cloud infrastructure.
- [ ] Tests pass.
- [ ] No regressions are introduced in the core API or current CLI/SDK behavior.

## CI / verification steps
- [ ] Run `python -m pytest tests/test_voice_adapter.py -v`.
- [ ] Run `python -m pytest`.
- [ ] Run `python examples/openclaw_voicedemo.py`.
- [ ] Run repo linting (`ruff` or project-equivalent lint command).
- [ ] Run repo type checks (`mypy` or project-equivalent type command), if configured.
- [ ] Confirm demo outputs exist and are non-empty.

## Manual QA steps
- [ ] Confirm these demo outputs exist and are non-empty:
  - [ ] `examples/openclaw/output/namshub_neutral.wav`
  - [ ] `examples/openclaw/output/david_friendly.wav`
  - [ ] `examples/openclaw/output/voss_flair.wav`
- [ ] Confirm the adapter loads presets per-agent as expected.
- [ ] Confirm the fallback/default preset behavior.
- [ ] Confirm the PR only touches the intended files.
- [ ] Confirm any repo lint/typecheck jobs still pass.

## Files changed and rationale
- `voicedna/openclaw_adapter.py` — new adapter layer for per-agent VoiceDNA preset routing.
- `examples/openclaw_voicedemo.py` — reproducible demo for three agents and three presets.
- `tests/test_voice_adapter.py` — unit/smoke coverage for preset selection, env loading, and synthesis.
- `README.md` — user-facing usage and demo notes.
- `CHANGELOG.md` — release note for the pilot.
- `IMPLEMENTATION_NOTE.md` — implementation details and rollout guidance.

## Reviewer checklist
- [ ] PR body links to `research/voicedna_integration_summary.md` and `research/implementation_checklist.md`.
- [ ] The opt-in design is clear and does not change default behavior.
- [ ] The demo is local-first and reproducible.
- [ ] Rollout and rollback instructions are present.
- [ ] License / asset usage is acceptable for any bundled voice assets.

## Demo assets / size check
- [ ] Demo WAVs present under `examples/openclaw/output/`.
- [ ] No WAV files exceed 5 MB, or any that do are handled via LFS / external hosting.

## Missing details to verify before merge
- [ ] Credentials or env vars needed for the real VoiceDNA backend, if any.
- [ ] Exact CI expectations for the repo, if not already documented.
- [ ] Whether any bundled voice assets have redistribution restrictions.

## Status
- Ready for PR: yes, if no blockers remain.
