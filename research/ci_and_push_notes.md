# VoiceDNA → OpenClaw CI and push notes

## Short answer
A short-lived PAT is **not required** for the current VoiceDNA branch as documented here, because the branch does **not** modify `.github/workflows/*`.

Use a PAT only if a later change adds workflow files or the push/PR flow explicitly needs token-based publishing.

## What the current branch needs
Current branch: `feature/voicedna-openclaw-per-agent-voices`

Required token scopes if a token-based push/PR is used:
- `contents:write` — push source/doc/test changes
- `pull_requests:write` — create/update PRs with `gh` or API
- `workflow` — **only** if `.github/workflows/*` is changed

## Exact push / PR steps
From the VoiceDNA repo root:

```bash
cd /home/namshub/dev/VoiceDNA

git status --short --branch
git add research/final_integration_checklist.md research/ci_and_push_notes.md research/demo_commands.sh research/voice_license_report.md
git commit -m "docs: finalize VoiceDNA OpenClaw integration research"
git push -u origin feature/voicedna-openclaw-per-agent-voices
```

If the push succeeds and a PR is needed:

```bash
cd /home/namshub/dev/VoiceDNA
gh pr create \
  --repo lukejmorrison/VoiceDNA \
  --base main \
  --head feature/voicedna-openclaw-per-agent-voices \
  --title "Per-agent OpenClaw voice pilot" \
  --body-file research/final_integration_checklist.md
```

## If a PAT becomes necessary later
Use the smallest practical scope and keep it short-lived.

Minimal approval text for Luke to paste:

> Approve a short-lived GitHub PAT with `contents:write` and `pull_requests:write` for the VoiceDNA push/PR. Add `workflow` only if workflow files are changed.

## Safer fallback options if push is blocked
1. User-side push from Luke's machine.
2. Git bundle handoff instead of secret-based pushing.
3. PAT push only after explicit approval.

## Important note
This branch does **not** currently require `workflow` scope. Add it only if a future diff touches `.github/workflows/*`.
