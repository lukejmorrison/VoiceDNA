# DEPLOY_NOTES.md — VoiceDNA OpenClaw Integration

**Branch:** `feature/voicedna-openclaw-integration`  
**Author:** Dr Voss Thorne  
**Date:** 2026-04-18  
**Status:** ✅ Local validation complete — all tests green

---

## What this branch adds

| File | Purpose |
|------|---------|
| `voicedna/openclaw_live_voice.py` | `render_agent_voice()` — top-level entry point for the per-agent voice pipeline. Lazy singleton `VoiceAdapter` with env override support. |
| `tests/test_openclaw_live_voice.py` | 12 integration tests: preset map, singleton, env override, file write, per-agent routing. |

**Prior files (already on origin/main):**

| File | Purpose |
|------|---------|
| `voicedna/openclaw_adapter.py` | `VoiceAdapter` class + preset registry (`neutral`, `friendly`, `flair`) |
| `tests/test_voice_adapter.py` | 18 unit tests for `VoiceAdapter` |
| `examples/openclaw/voicedna_tts_hook.py` | Alternate encrypted `.voicedna.enc` hook pattern |
| `examples/openclaw_voicedemo.py` | Demo script: 3 agents × 3 presets → WAV files |

---

## Local validation results

```
pytest tests/test_voice_adapter.py tests/test_openclaw_live_voice.py -v
→ 30 passed in 1.93s

pytest (full suite)
→ 46 passed in 1.88s

ruff check voicedna/openclaw_live_voice.py tests/test_openclaw_live_voice.py
→ All checks passed!

render_agent_voice() live test — 3 agents, 3 WAVs written to demo/:
  agent:namshub      → neutral preset  → 163,754 bytes ✅
  agent:david-hardman → friendly preset → 165,516 bytes ✅
  agent:dr-voss-thorne → flair preset   → 189,688 bytes ✅
```

Demo WAVs: `demo/namshub.wav`, `demo/david-hardman.wav`, `demo/dr-voss-thorne.wav`  
Full validation log: `demo/validation_log_20260418.txt`

---

## Default agent → preset mapping

| Agent ID / Alias          | Preset   |
|---------------------------|----------|
| `agent:namshub` / `namshub` | `neutral` |
| `agent:david-hardman` / `david-hardman` | `friendly` |
| `agent:dr-voss-thorne` / `dr-voss-thorne` | `flair` |

Override at runtime:

```bash
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:new-agent":"flair"}'
```

Any agent not in the map or env override falls back to `neutral`.

---

## Wiring into the live OpenClaw voice pipeline

### Option A — Programmatic (recommended)

```python
from voicedna.openclaw_live_voice import render_agent_voice

# Inside any OpenClaw TTS output handler:
wav_bytes = render_agent_voice(
    text=tts_text,
    agent_id="agent:dr-voss-thorne",
    agent_name="dr-voss-thorne",
)
# Deliver wav_bytes to the channel's audio delivery mechanism.
```

### Option B — Env-driven (zero-code)

```bash
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:dr-voss-thorne":"flair"}'
```

Set these in the OpenClaw agent's environment before starting the gateway.

### Option C — Full OpenClaw skill/plugin hook

Use `examples/openclaw/voicedna_tts_hook.py` as a model.  
Register `process_tts_output` or `wrap_tts_provider` as an OpenClaw TTS post-processor.  
The skill follows the `audio-responder-tts` pattern: hook into the outbound TTS stage, not the inbound transcription stage.

---

## Deployment checklist

- [ ] Merge `feature/voicedna-openclaw-per-agent-voices` → `main` (already on origin)
- [ ] Merge `feature/voicedna-openclaw-integration` → `main`
- [ ] Re-run `python -m pytest` in deployment environment
- [ ] Set `VOICEDNA_OPENCLAW_PRESETS=1` in OpenClaw agent env
- [ ] Add any new agent IDs to `DEFAULT_AGENT_PRESET_MAP` in `openclaw_live_voice.py` or via env
- [ ] If using production TTS backend (PersonaPlexTTS / PiperTTS / RVC), configure the provider before calling `render_agent_voice`

---

## Rollback

Complete rollback removes all integration code without affecting any existing VoiceDNA behavior:

```bash
git revert HEAD~2..HEAD   # or reset to the pre-integration commit

# Manual alternative:
rm voicedna/openclaw_live_voice.py
rm tests/test_openclaw_live_voice.py
```

All existing `voicedna/` code paths are unaffected — the integration is strictly additive.

---

## Remote push / PR

The branch is already at `origin/feature/voicedna-openclaw-integration`.

To open a PR:

```bash
cd /home/namshub/dev/VoiceDNA
gh pr create \
  --base main \
  --head feature/voicedna-openclaw-integration \
  --title "feat: wire VoiceDNA VoiceAdapter into live OpenClaw per-agent voice pipeline" \
  --body "Adds \`render_agent_voice()\` entry point (\`voicedna/openclaw_live_voice.py\`) and 12 integration tests. 46/46 tests pass locally. Per-agent preset routing: namshub→neutral, david-hardman→friendly, dr-voss-thorne→flair. Env override via VOICEDNA_OPENCLAW_PRESETS_MAP. See DEPLOY_NOTES.md for wiring options and rollback."
```

If push/auth is required for new commits, set the remote with a PAT:

```bash
git remote set-url origin https://<YOUR_PAT>@github.com/lukejmorrison/VoiceDNA.git
git push origin feature/voicedna-openclaw-integration
```

---

## CI

CI workflow: `.github/workflows/ci.yml`  
The branch is on origin — CI runs on push. No GitHub Actions workflow modifications are required by this integration.
