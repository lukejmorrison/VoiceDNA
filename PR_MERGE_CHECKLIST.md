# VoiceDNA PR #5 — Merge Checklist

Branch: `feature/voicedna-openclaw-per-agent-voices`
Scope check: **no `.github/workflows/*` files changed** in this PR diff, so a PAT with `workflow` scope is **not required** for the current branch state.

## 1) Current status snapshot
- [x] PR is limited to source/docs/tests/demo assets.
- [x] No workflow files are touched (`.github/workflows/*` not present in branch diff).
- [x] Demo WAVs exist in `examples/openclaw/output/`.
- [ ] Full upstream CI status must still be confirmed after push/PR creation.
- [ ] Final maintainer review still needed.

## 2) Local commands to run before merge
Run from repo root:

```bash
cd /home/namshub/dev/VoiceDNA

git status --short --branch
git diff --name-only origin/main...HEAD
python -m pytest tests/test_voice_adapter.py -v
python -m pytest
action=lint
ruff check voicedna/openclaw_adapter.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py
```

If the repo uses format/type checks, run the project-equivalent commands as well, for example:

```bash
ruff format --check .
mypy voicedna/openclaw_adapter.py
```

## 3) Pass/fail checkpoints
- [ ] `tests/test_voice_adapter.py` passes.
- [ ] Full `python -m pytest` passes, or known unrelated failures are documented.
- [ ] Lint passes on all PR files.
- [ ] Demo script runs locally:

```bash
python examples/openclaw_voicedemo.py
```

- [ ] Generated demo WAVs are non-empty and readable.
- [ ] `VoiceAdapter` remains opt-in and does not change default CLI/SDK behavior.
- [ ] No unintended files are included in the PR.

## 4) Change log entry
Verify the release note / changelog entry is present and accurate.

Suggested check:

```bash
git diff origin/main...HEAD -- CHANGELOG.md IMPLEMENTATION_NOTE.md README.md
```

Expected content:
- per-agent OpenClaw voice routing
- 3 presets: `neutral`, `friendly`, `flair`
- opt-in behavior
- local-first demo path

## 5) Tag / release steps
After approval and merge:

```bash
cd /home/namshub/dev/VoiceDNA
git checkout main
git pull --ff-only

git tag -a voicedna-v2.9.8 -m "VoiceDNA per-agent voice pilot"
git push origin voicedna-v2.9.8
```

If the release process uses a different version/tag, update the tag name to match the repo’s release convention.

## 6) PAT requirement check
### Current PR
- **PAT with `workflow` scope: NOT required**
- Reason: this PR does not modify any workflow files.

### If a future revision touches `.github/workflows/*`
Use a PAT with at least:
- `contents:write`
- `pull_requests:write` if using `gh` or the GitHub API to create/update the PR
- `workflow` if any file under `.github/workflows/` is added or modified

### Minimal GitHub PAT request text to paste
If workflow changes are added later, paste this into the GitHub PAT notes / request:

> Create a Personal Access Token with repository write access for VoiceDNA. Required scopes: `contents:write` for push, `pull_requests:write` if PR creation/update will use the token, and `workflow` only if any `.github/workflows/*` files are changed. Set the shortest practical expiry.

## 7) User-facing approval text for PAT request
Use this only if workflow-file changes appear later:

> I need a PAT to push/merge this PR because it touches `.github/workflows/*`. Please create a token with `contents:write` and `workflow` scope, plus `pull_requests:write` if you want me to create/update the PR with `gh`. Use the shortest expiry you’re comfortable with.

## 8) Alternative path: git bundle fallback
If token-based push is blocked, use the existing bundle path.

### Create bundle on the source machine
```bash
cd /home/namshub/dev/VoiceDNA
git bundle create /tmp/voicedna_openclaw_per_agent_voices.bundle HEAD feature/voicedna-openclaw-per-agent-voices
```

### Import bundle on the target machine
```bash
mkdir -p /tmp/voicedna-import
cd /tmp/voicedna-import
git clone /tmp/voicedna_openclaw_per_agent_voices.bundle voicedna-import
cd voicedna-import
git checkout feature/voicedna-openclaw-per-agent-voices
```

### Fetch into an existing clone
```bash
cd /path/to/existing/clone
git fetch /path/to/voicedna_openclaw_per_agent_voices.bundle feature/voicedna-openclaw-per-agent-voices:feature/voicedna-openclaw-per-agent-voices
git checkout feature/voicedna-openclaw-per-agent-voices
```

### Push from the target clone
```bash
cd /path/to/clone
git push -u origin feature/voicedna-openclaw-per-agent-voices
```

## 9) Merge decision gate
Do not merge until all of the following are true:
- [ ] local tests and lint pass, or known non-blocking failures are documented
- [ ] CI is green, or CI failures are clearly unrelated and accepted
- [ ] changelog/release notes are up to date
- [ ] no workflow files were unintentionally added
- [ ] maintainer approval is recorded
