# RELEASE CHECKLIST — VoiceDNA v3.1.0 (Per-Agent Voice Pilot)

Date: 2026-04-18  
Branch: `feature/voicedna-openclaw-per-agent-voices` (merged → main via PR #5)  
Engineer: Dr Voss Thorne

## Pre-release

- [x] `DESIGN_DOC.md` finalized and committed
- [x] `voicedna/openclaw_adapter.py` — `VoiceAdapter` class implemented
- [x] `examples/openclaw_voicedemo.py` — demo script produces 3 WAVs
- [x] `tests/test_voice_adapter.py` — 18 unit/smoke tests pass (0 failures)
- [x] `tests/test_consistency_engine.py` — 2 tests pass
- [x] `tests/test_piper_quality.py` — passes (3 skipped: backend not installed; expected)
- [x] `IMPLEMENTATION_NOTE.md` committed
- [x] `CHANGELOG.md` updated (v3.1.0 section added)
- [x] `README.md` updated with per-agent voice usage section
- [x] No breaking changes to existing public API

## CI

- [x] PR #5 merged (GitHub: lukejmorrison/VoiceDNA#5)
- [x] CI smoke: 20 passed, 3 skipped, 0 failed (pre-existing collection failures on 5 unrelated test files due to missing `cryptography` dep — not regressed by this PR)

## Demo Artifacts

- [x] `demo/namshub_neutral.wav` — 164,696 bytes
- [x] `demo/david_friendly.wav` — 211,876 bytes
- [x] `demo/voss_flair.wav` — 209,542 bytes
- [x] `demo/README.md` — verification checklist and regeneration instructions

## Post-merge

- [x] `reports/local_test_report.txt` — full local test output saved
- [x] `RELEASE_CHECKLIST.md` — this file
- [x] PR #5 merged to main (not draft; all CI checks visible)

## Known Limitations / Follow-ups

- Synthesis backend is stub-based (PCM silence with WAV headers); real Piper/espeak backend integration is a follow-up task.
- 5 test files have pre-existing collection failures due to missing `cryptography` dep in CI; tracked separately.
- Voice presets are hardcoded; env-based override (`VOICEDNA_AGENT_PRESETS`) is implemented but not fully documented.
