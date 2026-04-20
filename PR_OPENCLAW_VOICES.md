# PR: VoiceDNA → OpenClaw Per-Agent Voice Pilot

**Branch:** `feature/voicedna-openclaw-per-agent-voices` → `main`  
**Repo:** `lukejmorrison/VoiceDNA`  
**Status:** Ready for review — awaiting Namshub sign-off before merge  
**Updated:** 2026-04-19

---

## Summary

Wire VoiceDNA's `VoiceAdapter` into the OpenClaw agent voice pipeline so each
agent can be assigned a distinct voice preset (`neutral`, `friendly`, `flair`)
at runtime. Fully opt-in — no change to existing VoiceDNA CLI/SDK behavior.

---

## Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| **DESIGN_DOC** | `DESIGN_DOC.md` (this repo, branch) | Architecture, config, backward-compat, changelog, **David's edge-case checklist** |
| **David's Integration Plan** | `research/openclaw_integration_plan.md` | David Hardman's wiring plan + test strategy |
| **Implementation Checklist** | `research/implementation_checklist.md` | Step-by-step verification (start here) |
| **Integration Summary** | `research/voicedna_integration_summary.md` | Research-stage summary and compatibility notes |
| **OpenClaw branch** | `lukejmorrison/openclaw` @ `feature/voicedna-openclaw-wiring` | Companion branch — shim, tests, CI |

---

## Changed Files (VoiceDNA repo)

| File | Status | Purpose |
|------|--------|---------|
| `voicedna/openclaw_adapter.py` | Existing | `VoiceAdapter`: preset selection + synthesis |
| `voicedna/openclaw_live_voice.py` | Existing | `render_agent_voice()` — opt-in live pipeline hook |
| `examples/openclaw_voicedemo.py` | Existing | Demo: 3 agents × 3 presets → WAV |
| `examples/openclaw/output/*.wav` | Refreshed | Validated demo WAV artifacts |
| `tests/test_voice_adapter.py` | Existing | 18 unit/smoke tests |
| `tests/test_openclaw_live_voice.py` | Existing | 18 integration tests |
| `DESIGN_DOC.md` | Updated | Added David's 5-item edge-case validation checklist |
| `.github/workflows/ci.yml` | Updated (local only) | Adds adapter compile-check + opt-in smoke step |
| `research/` | Updated | Prep artifacts, integration plan, smoke scripts |

### ⚠️ CI Workflow Blocker

The CI workflow update (`.github/workflows/ci.yml`) requires a GitHub PAT with
**`workflow` scope** to push. The commit is staged locally at HEAD on the
branch. To push it:

1. Generate a PAT with `repo` + `workflow` scopes at
   GitHub → Settings → Developer Settings → Personal Access Tokens
2. Run:
   ```bash
   cd /home/namshub/dev/VoiceDNA
   git push origin feature/voicedna-openclaw-per-agent-voices
   ```
3. Or apply the patch manually:
   ```bash
   git apply /tmp/voicedna_ci_workflow.patch
   git add .github/workflows/ci.yml
   git commit -m "ci: apply openclaw adapter smoke step"
   git push origin feature/voicedna-openclaw-per-agent-voices
   ```

---

## Changed Files (OpenClaw repo — companion branch)

| File | Status | Purpose |
|------|--------|---------|
| `tools/voicedna_adapter.py` | Existing | Local shim: `get_voice_adapter()`, `is_voicedna_enabled()` |
| `tools/voicedna_tts_hook.py` | Existing | Drop-in TTS hook for OpenClaw pipeline |
| `tools/voicedna_registry.py` | Existing | Registry CRUD CLI |
| `skills/voice-dna-registry/registry.json` | Existing | Per-agent voice config store |
| `tests/test_voicedna_adapter.py` | Existing | 27 adapter unit tests |
| `tests/test_voicedna_tts_hook.py` | Existing | 18 TTS hook tests |
| `tests/test_voicedna_e2e.py` | Existing | 9 E2E integration tests |
| `.github/workflows/ci.yml` | Existing | Full CI: checkout VoiceDNA, compile, test, smoke |
| `VOICEDNA_RUNBOOK.md` | Updated | Refreshed runbook + rollback steps |

---

## Test Evidence

### VoiceDNA repo

```
tests/test_voice_adapter.py        18 passed
tests/test_openclaw_live_voice.py  18 passed (+ 16 from other test files)
Total: 52 passed in 1.98s
```

### OpenClaw repo

```
tests/test_voicedna_adapter.py     27 passed
tests/test_voicedna_tts_hook.py    18 passed
tests/test_voicedna_e2e.py          9 passed
Total: 54 passed in 1.77s
```

### Demo WAVs (validated RIFF PCM 16-bit mono 22050 Hz)

| File | Size | Frames |
|------|------|--------|
| `namshub_neutral.wav` | 164,696 bytes | 82,326 |
| `david_friendly.wav` | 211,876 bytes | 105,916 |
| `voss_flair.wav` | 209,542 bytes | 104,749 |

---

## Configuration

```bash
# Enable per-agent voices
export VOICEDNA_OPENCLAW_PRESETS=1
# Optional: override default preset map
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

Default pilot map is baked in — no env vars needed for the three pilot agents.

---

## Backward Compatibility

- `render_agent_voice()` returns `None` when `VOICEDNA_OPENCLAW_PRESETS` is unset.
- No existing VoiceDNA module imports the new adapter files.
- All changes are additive — no existing public API was modified.

---

## Rollback

1. `unset VOICEDNA_OPENCLAW_PRESETS`
2. `unset VOICEDNA_OPENCLAW_PRESETS_MAP`
3. Remove the `render_agent_voice()` call from the OpenClaw TTS hook.
4. No schema migration or persistent state to clean up.

---

## Merge Gate

- [ ] Namshub final sign-off (do not merge without this)
- [ ] CI green on GitHub (unblock by pushing workflow commit with `workflow`-scoped PAT)
- [ ] David's 5 edge-case items confirmed (see `DESIGN_DOC.md`)
