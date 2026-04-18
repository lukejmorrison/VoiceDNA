# RELEASE CHECKLIST — VoiceDNA v3.1.0

Date: 2026-04-18  
Repo: `lukejmorrison/VoiceDNA`  
Target change: PR #5 (`feature/voicedna-openclaw-per-agent-voices`)  
Release recommendation: `v3.1.0`

## Goal
Ship the OpenClaw per-agent voice pilot as an additive release, with no default-behavior changes.

## Evidence to carry into release approval

- `gh pr checks 5 --repo lukejmorrison/VoiceDNA` → `test` **PASS**
- `gh pr view 5 --repo lukejmorrison/VoiceDNA --json statusCheckRollup` → `test` **SUCCESS**
- `python -m pytest tests/test_voice_adapter.py -v` → `15 passed, 3 skipped`
- `python -m pytest` → `34 passed, 0 failed`
- Failing checks recorded: **none on PR #5**; later `.github/workflows/feedback-helper.yml` failures on `main` are unrelated and should not block this release

## Merge PR #5

1. Fetch and inspect the branch:
   ```bash
   git fetch origin
   gh pr view 5 --repo lukejmorrison/VoiceDNA
   gh pr checks 5 --repo lukejmorrison/VoiceDNA
   ```
2. Merge PR #5 only after human approval:
   ```bash
   gh pr merge 5 --repo lukejmorrison/VoiceDNA --squash --delete-branch
   ```
3. Pull the updated `main` locally:
   ```bash
   git checkout main
   git pull --ff-only origin main
   ```

## Update release notes

1. Verify the `CHANGELOG.md` top entry still matches the shipped behavior:
   - `voicedna/openclaw_adapter.py`
   - `examples/openclaw_voicedemo.py`
   - `tests/test_voice_adapter.py`
   - `README.md` pilot section
2. If anything drifted, edit `CHANGELOG.md` and `README.md` before tagging.
3. Keep the release notes minimal and factual: opt-in behavior, deterministic preset routing, three presets (`neutral`, `friendly`, `flair`), and local demo WAVs.

## Tag the release

Use semantic versioning `v3.1.0` for this pilot release.

```bash
git tag -a v3.1.0 -m "VoiceDNA v3.1.0: OpenClaw per-agent voice pilot"
git push origin v3.1.0
```

## Publish the GitHub release

Prefer GitHub release notes generated from the changelog section.

```bash
awk 'BEGIN{p=0} /^## \[3\.1\.0\]/{p=1; next} /^## \[/{if(p){exit}} p{print}' CHANGELOG.md > /tmp/voicedna-v3.1.0-notes.md
gh release create v3.1.0 --repo lukejmorrison/VoiceDNA --title "VoiceDNA v3.1.0" --notes-file /tmp/voicedna-v3.1.0-notes.md
```

## Post-release verification

- [ ] Confirm the release tag exists on GitHub and locally
- [ ] Confirm the release page shows the `3.1.0` notes from `CHANGELOG.md`
- [ ] Run a quick smoke test from `main`
- [ ] Confirm no unintended generated files were published
- [ ] Notify the team that the pilot is live

## Human approvals required

- [ ] Approve merge of PR #5
- [ ] Approve creation and push of tag `v3.1.0`
- [ ] Approve publication of the GitHub release

## Notes

- This release is additive and opt-in by default.
- Full-repo validation is already green in local evidence (`34 passed`).
- If the release needs to be rolled back, revert the merge commit and delete the tag only with explicit approval.
