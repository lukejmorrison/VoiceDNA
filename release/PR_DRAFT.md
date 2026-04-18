# Per-agent OpenClaw voice presets — PR body

## Summary
This PR adds an opt-in OpenClaw adapter that maps individual agents to distinct VoiceDNA presets, plus a demo script and tests for the per-agent voice pilot.

## Changed files
- `voicedna/openclaw_adapter.py` — new `VoiceAdapter` layer and preset registry.
- `examples/openclaw_voicedemo.py` — local demo that generates three agent-specific WAVs.
- `tests/test_voice_adapter.py` — preset-selection, env-loading, and synthesis smoke coverage.
- `voicedna/__init__.py` — guards optional heavy imports so the lightweight adapter stays importable.
- `README.md` — usage and demo notes.
- `CHANGELOG.md` / `IMPLEMENTATION_NOTE.md` / `PR_CHECKLIST.md` / `PR_DESCRIPTION.md` — rollout and verification docs.
- `examples/openclaw/output/*.wav` — demo outputs included for review.

## Motivation
OpenClaw agents need distinct, recognizable voices without changing default VoiceDNA behavior. This pilot keeps the feature opt-in and local-first, with no cloud dependency for the demo path.

## Test results
- `python -m pytest -q` — **failed during collection** in this workspace because `cryptography` is missing.
- `python examples/openclaw_voicedemo.py` — **started** and resolved preset selection, but failed at synthesis because the VoiceDNA runtime backend is not importable in this environment.
- WAV validation: the existing demo files in `examples/openclaw/output/` are valid mono WAVs and were readable with Python’s `wave` module.

## Demo notes
- Demo outputs present:
  - `examples/openclaw/output/namshub_neutral.wav`
  - `examples/openclaw/output/david_friendly.wav`
  - `examples/openclaw/output/voss_flair.wav`
- The adapter and demo wiring are present and connected via `VoiceAdapter`.
- The branch remains opt-in via `VOICEDNA_OPENCLAW_PRESETS=1` / `VOICEDNA_OPENCLAW_PRESETS_MAP`.

## Follow-up checklist
- [ ] Install or expose the `voice_dna` / `cryptography` runtime dependencies in CI/local dev.
- [ ] Re-run `python -m pytest tests/test_voice_adapter.py -v`.
- [ ] Re-run `python -m pytest`.
- [ ] Re-run `python examples/openclaw_voicedemo.py` and regenerate demo WAVs if needed.
- [ ] Confirm CI workflow expectations and any repo-specific lint/typecheck commands.
- [ ] Reviewers: verify opt-in behavior, demo assets, and rollback path.
- [ ] Secrets: none needed for the local demo path; only required if CI or backend integration later introduces external services.
