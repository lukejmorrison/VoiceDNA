# VoiceDNA push plan

Branch: `feature/voicedna-openclaw-per-agent-voices`
Repo: `lukejmorrison/VoiceDNA`
Prepared by: David Hardman
Date: 2026-04-17

## What I verified

- Remote feature branch exists: `origin/feature/voicedna-openclaw-per-agent-voices`
- Local checkout is **4 commits behind** that remote branch
- Dry-run push failed with a **non-fast-forward** rejection:
  - `! [rejected] feature/voicedna-openclaw-per-agent-voices -> feature/voicedna-openclaw-per-agent-voices (fetch first)`
- No `.github/workflows/*` files are included in the branch diff, so **workflow scope is not required for the current branch contents**

## Why the push failed

This is a standard Git history divergence issue, not a permissions problem.

The remote branch already has newer commits:
- `4e073b0 docs: add DESIGN_DOC, research notes, release artifacts, and test logs for per-agent voices PR`
- `d8651df fix: guard voicedna/__init__ imports with try/except for optional heavy deps`
- `f9700c5 fix: make voice_dna import optional; skip synthesis tests without backend; fix lint`
- `f82eadf docs: prepare VoiceDNA PR materials`

Local HEAD is older than that tip, so a plain push is rejected until the histories are aligned.

## PAT / workflow-scope answer

### Does this branch need a PAT with `workflow` scope?

**No, not for the current branch contents.**

Reason:
- GitHub only requires workflow permission when you are pushing changes under `.github/workflows/*` or otherwise modifying workflow definitions.
- This branch changes app code, tests, docs, and release artifacts, but not workflow files.

### When would `workflow` scope be needed?

If a future commit adds or changes `.github/workflows/*`, then a classic PAT usually needs:
- `repo`
- `workflow`

For a fine-grained PAT, the repo needs write access to contents, plus the workflow-related permission if workflow files are edited.

## Decision matrix

| Option | What it does | Pros | Cons | Recommended? |
|---|---|---|---|---|
| A. Short-lived PAT | Push directly from this machine with HTTPS auth | Fast, familiar, one step to PR | Requires sharing a token with workflow questions only if workflows change | Good if Luke is comfortable with temporary token use |
| B. Bundle / patch import | Move the branch as a portable artifact, then push from the user's machine | No secrets, deterministic, safest for handoff | Slightly more manual | **Yes** - best balance of safety + friction |
| C. No push, manual PR in UI | Create/import locally, then use GitHub UI to open PR | Zero credential handling in assistant | Most manual, easiest to drift | Good fallback |

## Recommended path

**Option B: bundle/patch import.**

Why:
- avoids PAT handling entirely
- works even though the remote branch is already ahead of this checkout
- produces an auditable artifact Luke can move around safely

## Exact commands

### Option A - short-lived PAT

```bash
cd /home/namshub/.openclaw/workspaces/namshub/main/VoiceDNA

# confirm divergence first
git fetch origin feature/voicedna-openclaw-per-agent-voices
git rev-list --left-right --count origin/feature/voicedna-openclaw-per-agent-voices...HEAD

# push only after the remote/local branch state is intentionally aligned
GIT_ASKPASS=echo git push https://<username>:<PAT>@github.com/lukejmorrison/VoiceDNA.git feature/voicedna-openclaw-per-agent-voices

gh pr create \
  --repo lukejmorrison/VoiceDNA \
  --base main \
  --head feature/voicedna-openclaw-per-agent-voices \
  --draft \
  --title "feat: per-agent voice pilot — VoiceAdapter + OpenClaw demo (3 presets)" \
  --body-file PR_BODY.md
```

Minimal scopes:
- classic PAT: `repo`
- add `workflow` only if future commits touch `.github/workflows/*`

### Option B - bundle / patch import

Prepared artifacts:
- `release_prep/voicedna-20260417T1720EDT.bundle`
- `release_prep/voicedna-20260417T1720EDT.patch`

Import commands:

```bash
# bundle import
git fetch /path/to/voicedna-20260417T1720EDT.bundle feature/voicedna-openclaw-per-agent-voices:feature/voicedna-openclaw-per-agent-voices

# patch import from a clean clone
git checkout -b feature/voicedna-openclaw-per-agent-voices origin/main
git am < /path/to/voicedna-20260417T1720EDT.patch
```

### Option C - no push, manual PR body

1. Import the bundle or patch locally.
2. Open GitHub in the browser.
3. Select **Compare & pull request** for `feature/voicedna-openclaw-per-agent-voices`.
4. Mark it draft.
5. Paste `PR_BODY.md`.

## Files written

- `push-plan.md`
- `push-checklist.md`
- `PR_DRAFT.md`
- `PR_BODY.md`
- `release_prep/voicedna-20260417T1720EDT.bundle`
- `release_prep/voicedna-20260417T1720EDT.patch`

## Short summary for Luke

The branch is ready, but this local checkout is behind the remote feature branch, so a direct push is rejected. The safest no-secrets path is the prepared bundle/patch handoff; once Luke approves, that can be imported and pushed cleanly from a machine with normal GitHub auth.
