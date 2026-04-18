# PR Draft: feat: per-agent voice pilot — VoiceAdapter + OpenClaw demo (3 presets)

> **Status:** Ready for review, but this checkout is behind the remote feature branch.
> **Branch:** `feature/voicedna-openclaw-per-agent-voices` → `main`
> **Prepared:** 2026-04-17

## Current branch state

- `origin/feature/voicedna-openclaw-per-agent-voices` already exists on GitHub.
- This local checkout is **4 commits behind** that remote branch.
- A dry-run push from this checkout fails with a non-fast-forward rejection: `fetch first`.
- The branch diff does **not** include any `.github/workflows/*` files, so a PAT with `workflow` scope is **not required** for the current branch contents.

## PR Title

```text
feat: per-agent voice pilot — VoiceAdapter + OpenClaw demo (3 presets)
```

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

### Pilot Presets

| Preset | Agent | Voice Character |
|--------|-------|----------------|
| `neutral` | namshub | Balanced, clear |
| `friendly` | david | Warm, approachable |
| `flair` | voss | Crisp, authoritative |

### Compatibility

Feature is **opt-in only**. No default VoiceDNA behavior is altered unless the per-agent mapping config is explicitly set.

### How to Run the Demo

```bash
cd /home/namshub/.openclaw/workspaces/namshub/main/VoiceDNA
python examples/openclaw_voicedemo.py
ls -lh examples/openclaw/output/
```

### Test Results

- `python -m pytest -v --tb=short`
- Result: **34 passed**

### Lint / Type Status

- `py_compile`: PASS
- `ruff`: prior run cleaned formatting issues in the PR files
- `mypy`: `openclaw_adapter.py` clean; existing unrelated errors remain in `providers/` and `filters/`

### Large File Note

Demo WAVs are under 1MB each and are committed to the branch.

### Rollout / Rollback

**Rollout:**
1. Merge behind the opt-in config path only.
2. Validate demo and adapter in one pilot environment.
3. Keep current default presets and API surface unchanged.

**Rollback:**
1. Disable the opt-in mapping/config to revert to existing behavior.
2. Remove or ignore the demo path if the pilot needs to pause.
3. Revert this PR if any regression appears in core VoiceDNA behavior.

### Reviewer Checklist

- [ ] `VoiceAdapter.select_preset()` returns correct preset for each agent mapping
- [ ] `VoiceAdapter.synthesize()` produces non-empty WAV output
- [ ] Fallback to `neutral` preset works when agent not in mapping
- [ ] Env-driven opt-in config loads correctly
- [ ] Demo script runs end-to-end without errors
- [ ] No changes to existing public VoiceDNA API surface
- [ ] All 34 tests pass: `python -m pytest -q`
- [ ] README additions are clear and accurate
- [ ] CHANGELOG entry is correct
- [ ] No large binary files added unexpectedly (WAVs are <1MB each)
- [ ] Pre-existing mypy errors in `providers/` and `filters/` are not new to this PR

### Notes for the push/PR step

- Because the remote feature branch already exists and is ahead of this checkout, do **not** push this local HEAD directly.
- If you want to make the local checkout match the remote feature branch first, use:

```bash
git fetch origin feature/voicedna-openclaw-per-agent-voices
git switch feature/voicedna-openclaw-per-agent-voices
git reset --hard origin/feature/voicedna-openclaw-per-agent-voices
```

- After that, any **new** commits can be pushed normally.

---

_Prepared by David Hardman subagent — 2026-04-17_
