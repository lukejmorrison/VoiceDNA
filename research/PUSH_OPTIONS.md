# PUSH_OPTIONS — VoiceDNA per-agent voice pilot

Branch: `feature/voicedna-openclaw-per-agent-voices`
Run label: `voiceDNA-research-prep`

## Workflow-file check
- This branch does **not** touch any `.github/workflows/*` files relative to `origin/main`.
- So there is no workflow-permission push blocker from the current diff.

## If workflow files are added later
Expected push/review risk:
- GitHub may block workflow-file changes if the repo policy requires extra permission to create or modify Actions workflows.
- Common symptoms include a failed push or a PR warning about workflow permissions.

Example error text to watch for:
- `remote: error: GH006: Protected branch update failed for refs/heads/feature/voicedna-openclaw-per-agent-voices`
- A workflow-policy rejection mentioning `.github/workflows/*`

## Three safe unblock options
1. **Have the user push from their own machine**
   - Safest when they already have the right repo permissions.
   - Command:
     `git push -u origin feature/voicedna-openclaw-per-agent-voices`

2. **Use a short-lived PAT with the needed repo/workflow scope**
   - Only if the repository policy explicitly requires elevated workflow permission.
   - Example setup:
     `git remote set-url origin https://<token>@github.com/<owner>/<repo>.git`
   - Do not store the token in files or logs.

3. **Share a git bundle instead of pushing directly**
   - Create a portable branch snapshot and let the recipient import it.
   - Create bundle:
     `git bundle create /tmp/voicedna_openclaw_per_agent_voices.bundle HEAD feature/voicedna-openclaw-per-agent-voices`
   - Import on the target machine:
     `git clone /tmp/voicedna_openclaw_per_agent_voices.bundle voicedna-import`

## Recommendation
- Since this branch currently has no workflow-file changes, try a normal push first.
- If push fails for permission reasons, fall back to the bundle or user-push option above.
