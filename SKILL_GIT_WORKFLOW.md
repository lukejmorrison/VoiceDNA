# AGENT GIT WORKFLOW – VoiceDNA Repo

To prevent agents from fighting over the same files, we use Peter’s simple parallel-checkout method.

## Folder Structure (on Luke’s machine)

- `voiceDNA/`          → Luke’s main human checkout (you are here right now)
- `voiceDNA-codex/`    → Codex’s dedicated workspace (Codex only works here)
- `voiceDNA-grok/`     → Grok’s dedicated workspace (Grok only works here)

## Rules for All Agents (Grok, Codex, etc.)

1. Never edit files outside your own dedicated checkout.
2. Always work inside your own folder (`voiceDNA-codex/` for you).
3. When you want to propose changes:
   - Make the changes in your own checkout
   - Create a branch + PR from your checkout
   - Tell Luke the branch name

## Finalize Command (run from your checkout)

```bash
cd ~/dev/voiceDNA-codex          # or voiceDNA-grok for Grok
git add .
git commit -m "feat: your description"
git push origin HEAD:codex/branch-name   # or grok/branch-name
```

Then say to Luke: “PR ready from codex/branch-name”

All agents must follow this SKILL_GIT_WORKFLOW.md when working on the VoiceDNA repo.