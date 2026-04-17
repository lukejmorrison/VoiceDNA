#!/usr/bin/env bash
# push_voicedna_pr.sh
# Push branch and open PR for feature/voicedna-openclaw-per-agent-voices
# DO NOT run this script without explicit approval from Luke Morrison.

set -euo pipefail

BRANCH="feature/voicedna-openclaw-per-agent-voices"
REPO="lukejmorrison/VoiceDNA"   # adjust if fork differs
BASE_BRANCH="main"

echo "[push_voicedna_pr.sh] Pushing branch to remote..."
git push origin "$BRANCH"

echo "[push_voicedna_pr.sh] Opening PR via gh CLI..."
gh pr create \
  --repo "$REPO" \
  --base "$BASE_BRANCH" \
  --head "$BRANCH" \
  --title "Per-agent OpenClaw voice presets — feature/voicedna-openclaw-per-agent-voices" \
  --body-file "$(dirname "$0")/../PR_DRAFT.md"

echo "[push_voicedna_pr.sh] Done."
