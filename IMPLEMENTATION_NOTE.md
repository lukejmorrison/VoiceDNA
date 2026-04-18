# IMPLEMENTATION_NOTE.md — VoiceDNA → OpenClaw Live Voice Integration

**Branch:** `feature/voicedna-openclaw-integration`  
**Author:** Dr Voss Thorne (subagent)  
**Date:** 2026-04-18  
**Base:** `feature/voicedna-openclaw-per-agent-voices` (pilot) → committed here on `main`-derived branch

---

## What was implemented in this branch

| File | Role |
|------|------|
| `voicedna/openclaw_live_voice.py` | **New.** `render_agent_voice()` entry point — wires `VoiceAdapter` preset routing into the live agent voice pipeline. Default map: `agent:namshub→neutral`, `agent:david-hardman→friendly`, `agent:dr-voss-thorne→flair`. Singleton adapter; env override via `VOICEDNA_OPENCLAW_PRESETS_MAP`. |
| `tests/test_openclaw_live_voice.py` | **New.** 12 integration tests covering preset map, adapter singleton, env override, file write, and per-agent routing. |

**Prior pilot files (already on `feature/voicedna-openclaw-per-agent-voices` / origin/main):**

| File | Role |
|------|------|
| `voicedna/openclaw_adapter.py` | Core `VoiceAdapter` class + preset registry (`neutral`, `friendly`, `flair`) |
| `examples/openclaw_voicedemo.py` | Demo: 3 agents × 3 presets → WAV files |
| `examples/openclaw/voicedna_tts_hook.py` | Alternate hook pattern for encrypted `.voicedna.enc` flows |
| `tests/test_voice_adapter.py` | 18 unit tests for the adapter |

---

## Test results (this session)

```
pytest tests/test_openclaw_live_voice.py tests/test_voice_adapter.py -v
→ 30 passed in 1.84s

ruff check voicedna/openclaw_live_voice.py tests/test_openclaw_live_voice.py
→ All checks passed!

python -m py_compile voicedna/openclaw_live_voice.py tests/test_openclaw_live_voice.py
→ (no output — clean)
```

---

## Test commands (reproduce locally)

```bash
cd /home/namshub/dev/VoiceDNA

# Adapter unit tests (pilot)
python -m pytest tests/test_voice_adapter.py -v

# Live voice integration tests (this branch)
python -m pytest tests/test_openclaw_live_voice.py -v

# All 30 tests
python -m pytest tests/test_voice_adapter.py tests/test_openclaw_live_voice.py -v

# Lint
ruff check voicedna/openclaw_live_voice.py tests/test_openclaw_live_voice.py

# Demo (requires VoiceDNA runtime backend)
PYTHONPATH=. VOICEDNA_OPENCLAW_PRESETS=1 python examples/openclaw_voicedemo.py
```

---

## How to wire into OpenClaw (next steps)

### Option A — Programmatic (minimal, no OpenClaw plugin changes)

```python
from voicedna.openclaw_live_voice import render_agent_voice

# In the agent's TTS output handler:
wav_bytes = render_agent_voice(
    text=tts_text,
    agent_id="agent:dr-voss-thorne",
    agent_name="dr-voss-thorne",
)
# Pass wav_bytes downstream to audio delivery
```

### Option B — Env-driven override

```bash
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:my-new-agent":"flair"}'
```

Any agent not in the env map or the default map falls back to `neutral`.

### Option C — Full OpenClaw skill/plugin wiring

Use `examples/openclaw/voicedna_tts_hook.py` as a model. Register
`render_agent_voice` or `VoiceDNATTSHook.process_tts_output` as an OpenClaw
TTS post-processor hook. See comments in that file for decorator and function
export patterns.

---

## Deployment checklist

- [ ] Merge `feature/voicedna-openclaw-per-agent-voices` → `main` first (it's on origin already).
- [ ] Then merge `feature/voicedna-openclaw-integration` → `main` (this branch — local only unless pushed or bundle applied).
- [ ] Re-run `python -m pytest` (full suite) in the deployment environment.
- [ ] If using production TTS backend (PersonaPlexTTS / PiperTTS / RVC), swap `adapter._tts` before calling `render_agent_voice`.
- [ ] Set `VOICEDNA_OPENCLAW_PRESETS=1` in the OpenClaw agent environment to signal opt-in mode.
- [ ] Add any new agent IDs to `DEFAULT_AGENT_PRESET_MAP` in `openclaw_live_voice.py` or supply via `VOICEDNA_OPENCLAW_PRESETS_MAP`.

---

## Rollback

- Remove or unimport `voicedna/openclaw_live_voice.py`.
- Delete `tests/test_openclaw_live_voice.py`.
- All existing `voicedna/` code paths remain unaffected.

---

## Pushing to origin (PAT required)

Push is blocked without a PAT (HTTPS remote, no stored credential).

**If you provide a PAT:**
```bash
cd /home/namshub/dev/VoiceDNA
git remote set-url origin https://<YOUR_PAT>@github.com/lukejmorrison/VoiceDNA.git
git push origin feature/voicedna-openclaw-integration
```

**Or apply the git bundle (no PAT needed on this machine):**

A bundle has been created at `/tmp/voicedna_integration.bundle`.

On any machine with the VoiceDNA repo cloned:
```bash
# Fetch the branch from the bundle
git fetch /tmp/voicedna_integration.bundle feature/voicedna-openclaw-integration:feature/voicedna-openclaw-integration

# Push to origin (requires auth on that machine)
git push origin feature/voicedna-openclaw-integration
```

Or open a PR manually via GitHub UI after pushing.
