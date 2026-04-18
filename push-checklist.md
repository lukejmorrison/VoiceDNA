# Push checklist for Luke

Branch: `feature/voicedna-openclaw-per-agent-voices`
Repo: `https://github.com/lukejmorrison/VoiceDNA.git`

## What we confirmed

- The remote feature branch already exists on GitHub.
- This local checkout is **4 commits behind** the remote feature branch.
- A dry-run push from this checkout was rejected with:
  - `! [rejected] feature/voicedna-openclaw-per-agent-voices -> feature/voicedna-openclaw-per-agent-voices (fetch first)`
- That means the blocker is **non-fast-forward history**, not workflow permissions.
- The branch contents do **not** include `.github/workflows/*`, so a PAT with `workflow` scope is **not needed** for the current branch contents.

## Minimal approval text Luke can send

Use this exact one-line approval if you want me to continue with a safe rebase/reset-and-push flow:

> Approved: sync with `origin/feature/voicedna-openclaw-per-agent-voices`, then push the updated branch and open the draft PR.

## Option A: user-supplied short-lived PAT

Only needed if you want me to push from this machine using HTTPS credentials.

### Minimal scopes

- Classic PAT: `repo`
- Add `workflow` only if you add or modify `.github/workflows/*` files in the branch
- Fine-grained PAT: repository access to this repo, with `Contents: Read and write`; add workflow-related permission only if workflow files change

### Copy/paste commands

```bash
cd /home/namshub/.openclaw/workspaces/namshub/main/VoiceDNA

git fetch origin feature/voicedna-openclaw-per-agent-voices
# review the remote tip before moving local HEAD

git log --oneline --decorate --left-right origin/feature/voicedna-openclaw-per-agent-voices...HEAD

# If you want to align this checkout to the remote branch first:
# git reset --hard origin/feature/voicedna-openclaw-per-agent-voices

# Push using a short-lived PAT when you are sure the remote branch state is correct
GIT_ASKPASS=echo git push https://<username>:<PAT>@github.com/lukejmorrison/VoiceDNA.git feature/voicedna-openclaw-per-agent-voices

gh pr create \
  --repo lukejmorrison/VoiceDNA \
  --base main \
  --head feature/voicedna-openclaw-per-agent-voices \
  --draft \
  --title "feat: per-agent voice pilot — VoiceAdapter + OpenClaw demo (3 presets)" \
  --body-file PR_BODY.md
```

## Option B: bundle or patch for manual import

Use this if you want to move the branch without sharing credentials.

### Already prepared artifact

- `release_prep/voicedna-20260417T1720EDT.bundle`
- `release_prep/voicedna-20260417T1720EDT.patch`

### User-side commands

```bash
# import the branch bundle into a fresh clone or a spare worktree
cd /path/to/a/clone/of/VoiceDNA
git fetch /path/to/voicedna-20260417T1720EDT.bundle feature/voicedna-openclaw-per-agent-voices:feature/voicedna-openclaw-per-agent-voices

git switch feature/voicedna-openclaw-per-agent-voices
# if needed, push from the user's machine with their normal auth
# git push --set-upstream origin feature/voicedna-openclaw-per-agent-voices
```

Patch import alternative:

```bash
cd /path/to/clean/VoiceDNA-clone
git checkout -b feature/voicedna-openclaw-per-agent-voices origin/main
git am < /path/to/voicedna-20260417T1720EDT.patch
```

## Option C: prepare PR without pushing

Use this if you want Luke to open the PR in the GitHub UI later.

### Manual steps

1. Open the repo in GitHub.
2. Create or update the branch `feature/voicedna-openclaw-per-agent-voices` from the imported bundle/patch or your own local clone.
3. Go to the Pull Requests tab.
4. Click **New pull request**.
5. Set base to `main` and compare to `feature/voicedna-openclaw-per-agent-voices`.
6. Paste the body from `PR_BODY.md`.
7. Mark as draft.

## Recommendation

**Least-friction safe path: Option B.**

Why:
- No secrets to manage
- No PAT scope questions
- Preserves the exact branch state in a portable artifact
- Safe even when the remote branch is already ahead of this checkout

## Short verdict for Luke

The blocker is not GitHub workflow permissions; it is a branch divergence/non-fast-forward issue. The safest next step is to import the prepared bundle or patch, then push from a machine with normal GitHub auth once Luke approves.
