# PR Draft: feat: per-agent voice pilot — VoiceAdapter + OpenClaw demo (3 presets)

> **Status:** Ready for review — awaiting Luke's approval to push and open PR.
> **Branch:** `feature/voicedna-openclaw-per-agent-voices` → `main`
> **Prepared:** 2026-04-13 by Dr Voss Thorne

---

## PR Title

```
feat: per-agent voice pilot — VoiceAdapter + OpenClaw demo (3 presets)
```

---

## PR Body

### Summary

This PR delivers the VoiceDNA per-agent voice pilot. It adds an opt-in `VoiceAdapter` layer so OpenClaw agents can speak with distinct VoiceDNA presets, plus a runnable demo and full unit/smoke test coverage.

### Rationale

- Enable per-agent voice routing without changing existing VoiceDNA CLI/SDK defaults.
- Prove the pilot with local-first demo output and repeatable tests.
- Keep the integration strictly additive and low-risk for the core API.

### What Changed

| File | Change |
|------|--------|
| `voicedna/openclaw_adapter.py` | New `VoiceAdapter` class — preset selection, synthesis, per-agent mapping, env-driven opt-in |
| `examples/openclaw_voicedemo.py` | Demo: 3 agents × 3 presets → WAV output |
| `tests/test_voice_adapter.py` | 17 unit tests: preset selection, fallback, env loading, synthesis smoke |
| `conftest.py` | Root conftest for pytest path resolution |
| `README.md` | Per-agent voices section added |
| `CHANGELOG.md` | Entry for this feature |
| `IMPLEMENTATION_NOTE.md` | Implementation context and design decisions |

**Commits (5) ahead of main:**
```
14dcb76 style: apply ruff format to PR files (openclaw_adapter, test_voice_adapter, conftest)
19d3388 fix: add root conftest.py for pytest path resolution; fix demo sys.path; remove unused imports
ccc2eef docs: add per-agent voices README section, CHANGELOG entry, IMPLEMENTATION_NOTE
7c03e95 feat: add OpenClaw per-agent voice demo (3 agents × 3 presets → WAV)
e677b8c feat: add VoiceAdapter (select_preset + synthesize) with 3 pilot presets
```

### Pilot Presets

| Preset | Agent | Voice Character |
|--------|-------|----------------|
| `neutral` | namshub | Balanced, clear |
| `friendly` | david | Warm, approachable |
| `flair` | voss | Crisp, authoritative |

### Compatibility

Feature is **opt-in only**. No default VoiceDNA behavior is altered unless the per-agent mapping config is explicitly set.

---

## How to Run the Demo

```bash
cd /home/namshub/.openclaw/workspaces/namshub/main/VoiceDNA

# Run demo (generates 3 WAV files)
python examples/openclaw_voicedemo.py

# Verify outputs are non-empty
ls -lh examples/openclaw/output/
# Expected:
#   namshub_neutral.wav   (~164K)
#   david_friendly.wav    (~208K)
#   voss_flair.wav        (~208K)
```

---

## Test Results

```bash
python -m pytest -v --tb=short
# Result: 34 passed in ~1.83s
```

Full output: `TEST_LOG.txt` (repo root) or `/home/namshub/dev/VoiceDNA/TEST_LOG.txt`

---

## Lint / Type Status

- **py_compile:** PASS — all files syntax-clean
- **ruff (prior run):** 2 unused imports auto-fixed; 0 errors remaining
- **mypy:** `openclaw_adapter.py` clean; 4 pre-existing errors in `providers/` and `filters/` (not introduced by this PR)

Full output: `LINT_LOG.txt` (repo root) or `/home/namshub/dev/VoiceDNA/LINT_LOG.txt`

---

## Large File Note

Demo WAVs are **under 1MB each** — no LFS required:
- `examples/openclaw/output/namshub_neutral.wav` — 164K
- `examples/openclaw/output/david_friendly.wav` — 208K
- `examples/openclaw/output/voss_flair.wav` — 208K

These are committed to the branch. If the repo introduces policy against committing audio output files in the future, move them to `.gitignore` and document regeneration steps.

---

## Rollout / Rollback

**Rollout:**
1. Merge behind the opt-in config path only.
2. Validate demo and adapter in one pilot environment.
3. Keep current default presets and API surface unchanged.

**Rollback:**
1. Disable the opt-in mapping/config → reverts to existing behavior.
2. Remove or ignore demo path if pilot needs to pause.
3. Revert this PR if any regression appears in core VoiceDNA behavior.

---

## Reviewer Checklist

- [ ] `VoiceAdapter.select_preset()` returns correct preset for each agent mapping
- [ ] `VoiceAdapter.synthesize()` produces non-empty WAV output
- [ ] Fallback to `neutral` preset works when agent not in mapping
- [ ] Env-driven opt-in config loads correctly
- [ ] Demo script runs end-to-end without errors
- [ ] No changes to existing public VoiceDNA API surface
- [ ] All 34 tests pass: `python -m pytest -q`
- [ ] README additions are clear and accurate
- [ ] CHANGELOG entry is correct
- [ ] No large binary files added unexpectedly (WAVs are <1MB each — acceptable)
- [ ] Pre-existing mypy errors in `providers/` and `filters/` are NOT new to this PR

---

## Push Recipe (execute only after Luke's approval)

```bash
cd /home/namshub/.openclaw/workspaces/namshub/main/VoiceDNA

# Push branch
git push origin feature/voicedna-openclaw-per-agent-voices

# Open PR (GitHub CLI)
gh pr create \
  --base main \
  --head feature/voicedna-openclaw-per-agent-voices \
  --title "feat: per-agent voice pilot — VoiceAdapter + OpenClaw demo (3 presets)" \
  --body-file PR_DRAFT.md
```

---

_Prepared by Dr Voss Thorne subagent — 2026-04-13_
