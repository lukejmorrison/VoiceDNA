# Push Readiness — VoiceDNA

## Current branch status
- Local branch: `feature/voicedna-openclaw-per-agent-voices`
- Remote branch exists: `origin/feature/voicedna-openclaw-per-agent-voices`
- Local vs remote: `0` local commits ahead, `2` commits behind remote (`git rev-list --left-right --count feature/... ... origin/feature/...`)
- PR #5 exists on GitHub and is currently **MERGED**: <https://github.com/lukejmorrison/VoiceDNA/pull/5>

## Workflow file check
- Changed files under `.github/workflows/`: **none found**
- Therefore the GitHub `workflow` scope requirement does **not** appear to be triggered by this branch diff

## Recommended next step
- **No PAT needed for workflow scope** for the current diff.
- If you are just syncing local state before any new work, fetch/rebase first:

```bash
git fetch origin
git checkout feature/voicedna-openclaw-per-agent-voices
git rebase origin/feature/voicedna-openclaw-per-agent-voices
```

## Safe options to proceed

### A) Short-lived PAT push (only if a future commit touches `.github/workflows/`)
**Minimal scopes:** `repo` + `workflow`

```bash
git push https://x-access-token:$TOKEN@github.com/lukejmorrison/VoiceDNA.git feature/voicedna-openclaw-per-agent-voices
```

- **Pros:** direct, fastest path for protected workflow changes
- **Cons:** requires a secret token; do not reuse long-term

### B) Manual push via prepared git bundle
Create bundle on the source machine:

```bash
git bundle create /tmp/voicedna-openclaw-per-agent-voices.bundle origin/main..feature/voicedna-openclaw-per-agent-voices
```

Apply on the target machine, then push:

```bash
git fetch /tmp/voicedna-openclaw-per-agent-voices.bundle feature/voicedna-openclaw-per-agent-voices:feature/voicedna-openclaw-per-agent-voices
git push origin feature/voicedna-openclaw-per-agent-voices
```

- **Pros:** no PAT needed
- **Cons:** extra transfer step; only works if the target can reach origin

### C) Open / update PR in GitHub web UI
1. Open the repo PR page: <https://github.com/lukejmorrison/VoiceDNA/pulls>
2. Create a PR from `feature/voicedna-openclaw-per-agent-voices` into `main` if needed, or update the existing merged PR context with new commits on a new branch.
3. Push locally first if you have new commits:

```bash
git push origin feature/voicedna-openclaw-per-agent-voices
```

- **Pros:** no token handling in shell
- **Cons:** still needs a normal authenticated push unless the branch is already on GitHub
