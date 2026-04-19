# VoiceDNA → OpenClaw Integration Design

**Goal:** add per-agent voice presets to OpenClaw through `VoiceAdapter` without changing default TTS behavior.

## Approach
OpenClaw already has the right seam: `tools/voicedna_tts_hook.py` calls `voicedna.openclaw_live_voice.render_agent_voice()` and returns `None` when the opt-in flag is off. Keep that model: the VoiceDNA adapter is loaded lazily, only when `VOICEDNA_OPENCLAW_PRESETS=1` is set and the VoiceDNA repo is importable.

### Code touchpoints
- **VoiceDNA:** `voicedna/openclaw_adapter.py`, `voicedna/openclaw_live_voice.py`, `examples/openclaw_voicedemo.py`
- **OpenClaw shim:** `tools/voicedna_adapter.py` and `tools/voicedna_tts_hook.py`
- **Tests:** `tests/test_voicedna_adapter.py`, `tests/test_voicedna_tts_hook.py`, `tests/test_voicedna_e2e.py`

### Env/config
- `VOICEDNA_OPENCLAW_PRESETS=1` enables the feature.
- `VOICEDNA_OPENCLAW_PRESETS_MAP` optionally overrides the agent→preset map.
- Default mapping remains: `agent:namshub→neutral`, `agent:david-hardman→friendly`, `agent:dr-voss-thorne→flair`.
- Optional later secret: `VOICEDNA_PASSWORD_<AGENT>` only if encrypted `.voicedna.enc` assets are used; keep out of git.

### Feature-flag strategy
- Gate all VoiceDNA loading behind the env flag.
- If the flag is absent/falsy, `get_voice_adapter()` and `render_agent_voice()` both return `None` and OpenClaw stays on its current TTS path.
- Treat the adapter as additive; no core OpenClaw behavior changes.

### Rollout / rollback
**Rollout:**
1. Merge the adapter + hook + tests on a feature branch.
2. Run shim tests first, then E2E/demo smoke.
3. Enable `VOICEDNA_OPENCLAW_PRESETS=1` for a small pilot group.

**Rollback:**
1. Unset `VOICEDNA_OPENCLAW_PRESETS` and `VOICEDNA_OPENCLAW_PRESETS_MAP`.
2. Remove any live hook call site if one is added later.
3. Revert the integration commits if needed; no schema or data migration exists.
