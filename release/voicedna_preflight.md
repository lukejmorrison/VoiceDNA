# VoiceDNA preflight — `feature/voicedna-openclaw-per-agent-voices`

## Push path

```bash
cd /home/namshub/dev/VoiceDNA

git status --short --branch
git log --oneline --decorate -n 5

git push -u origin feature/voicedna-openclaw-per-agent-voices
```

If the branch is not yet on the remote, the first push above creates it and sets tracking.

## PAT scopes required

Use a PAT with at least:

- `contents:write` — required to push commits to the repository.
- `workflow` — required **if any files under `.github/workflows/` are added or modified**. GitHub treats workflow files as privileged because they can change CI execution and token behavior.
- `pull_requests:write` — only needed if the same token will be used to create or update the PR via API/`gh`.

For a classic PAT, the equivalent minimum is usually `repo` plus `workflow` for workflow-file changes.

## If push fails

### 1) Create a git bundle locally

```bash
cd /home/namshub/dev/VoiceDNA
git bundle create /tmp/voicedna_openclaw_per_agent_voices.bundle HEAD feature/voicedna-openclaw-per-agent-voices
```

### 2) Transfer the bundle to the target machine

Copy `/tmp/voicedna_openclaw_per_agent_voices.bundle` to the machine that can push or import the branch.

### 3) Apply the bundle on the target

```bash
mkdir -p /tmp/voicedna-import
cd /tmp/voicedna-import
git clone /tmp/voicedna_openclaw_per_agent_voices.bundle voicedna-import
cd voicedna-import
git checkout feature/voicedna-openclaw-per-agent-voices
```

If you need to update an existing clone instead:

```bash
cd /path/to/existing/clone
git fetch /path/to/voicedna_openclaw_per_agent_voices.bundle feature/voicedna-openclaw-per-agent-voices:feature/voicedna-openclaw-per-agent-voices
git checkout feature/voicedna-openclaw-per-agent-voices
```

### 4) Retry the push from the target clone

```bash
cd /path/to/clone
git push -u origin feature/voicedna-openclaw-per-agent-voices
```

## Short risk checklist

- [ ] Branch tip matches the intended recovered commit set.
- [ ] No accidental secrets, tokens, or local config files are staged.
- [ ] Demo assets or generated WAVs are not oversized for review.
- [ ] CI/workflow files are untouched unless the maintainer explicitly wants them.
- [ ] Any workflow-file change is pushed only with a PAT that includes `workflow`.
- [ ] The PR description clearly states the feature is opt-in and local-first.
