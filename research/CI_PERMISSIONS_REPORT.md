# CI / permissions report — VoiceDNA per-agent voice pilot

Branch: `feature/voicedna-openclaw-per-agent-voices`
Date: 2026-04-17

## Workflow review
Reviewed:
- `.github/workflows/ci.yml`
- `.github/workflows/feedback-helper.yml`
- `.github/workflows/auto-label-feedback.yml`
- `SKILL_GIT_WORKFLOW.md`

## Findings
- This branch does **not** modify any `.github/workflows/*` files relative to `origin/main`.
- Therefore, the current PR does **not** require workflow-file changes.
- The existing workflow files are ordinary CI/issue automation jobs and do not appear to be part of the branch diff.

## Required permissions for the current branch
If Luke pushes or creates the PR with a PAT / token-based flow, the practical minimum scopes are:
- `contents:write` — to push the source/doc/test changes
- `pull_requests:write` — if the token is used to create or update the PR via API / `gh`

## When `workflow` scope is needed
Add `workflow` scope only if a future revision:
- adds or edits files under `.github/workflows/*`
- needs to create, update, or trigger privileged Actions workflow definitions

Why it is needed:
- GitHub treats workflow-file changes as privileged repository actions.
- Without `workflow` scope, pushes/updates that touch workflow files may be rejected even if ordinary source writes are allowed.

## Safe command shortlist for Luke
From the repo root:

```bash
cd /home/namshub/dev/VoiceDNA

git status --short --branch
python -m pytest tests/test_voice_adapter.py -v
ruff check voicedna/openclaw_adapter.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py
```

If Luke wants to push the branch:

```bash
git push -u origin feature/voicedna-openclaw-per-agent-voices
```

If Luke wants to create the PR after push:

```bash
gh pr create \
  --repo lukejmorrison/VoiceDNA \
  --base main \
  --head feature/voicedna-openclaw-per-agent-voices \
  --title "Per-agent OpenClaw voice presets — feature/voicedna-openclaw-per-agent-voices" \
  --body-file PR_BODY.md
```

## Bottom line
- No workflow scope needed for the current diff.
- `workflow` scope is only a fallback requirement if workflow files are added later.
