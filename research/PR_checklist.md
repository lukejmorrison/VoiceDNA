# VoiceDNA per-agent voices — PR checklist

## Pre-push checks
- [ ] Sync this checkout to `origin/feature/voicedna-openclaw-per-agent-voices` first; this local branch is 4 commits behind the remote tip.
- [ ] Confirm the branch tip includes the expected delivery commits:
  - `f82eadf` — PR materials prep
  - `f9700c5` — optional import / test gating fix
  - `d8651df` — optional heavy deps guard in `voicedna/__init__.py`
  - `4e073b0` — research notes, release artifacts, and test logs
- [ ] Verify working tree is clean before any push.
- [ ] Confirm demo WAVs are present and non-empty:
  - `examples/openclaw/output/namshub_neutral.wav`
  - `examples/openclaw/output/david_friendly.wav`
  - `examples/openclaw/output/voss_flair.wav`

## CI smoke tests
- [ ] `python -m pytest -v --tb=short` passes.
- [ ] `python -m pytest -q tests/test_voice_adapter.py` passes quickly as a targeted smoke check.
- [ ] Run the OpenClaw demo script and confirm it emits the three WAVs.
- [ ] Optional lint smoke: `ruff check .` or the repo’s preferred lint command.

## Required secrets / auth
- [ ] GitHub auth for push + draft PR creation, if automation is used.
- [ ] If a PAT is needed, use a short-lived token with repo write access; add workflow permission only if `.github/workflows/*` changes are introduced.
- [ ] Do not store secrets in repo files or logs.

## Non-goals
- [ ] Do not change public VoiceDNA defaults unless explicitly intended.
- [ ] Do not add `.github/workflows/*` changes unless the PR scope expands.
- [ ] Do not push from the stale local HEAD without syncing to the remote feature branch first.
- [ ] Do not record or print secret values in notes or chat.
