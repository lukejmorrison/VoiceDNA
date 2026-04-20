# OpenClaw ↔ VoiceDNA Integration Plan

**Goal:** wire VoiceDNA’s `VoiceAdapter` into OpenClaw’s per-agent voice pipeline with the smallest possible change set, preserving default TTS behavior unless the feature is explicitly enabled.

**Sources used:**
- `VoiceDNA/research/voicedna_integration_summary.md`
- `VoiceDNA/research/implementation_checklist.md`
- `openclaw/docs/VOICE_DNA_HANDOFF.md`
- `openclaw/README.md` per-agent voice section
- `VoiceDNA/voicedna/openclaw_adapter.py`
- `VoiceDNA/voicedna/openclaw_live_voice.py`
- `VoiceDNA/examples/openclaw_voicedemo.py`
- `openclaw/tools/voicedna_adapter.py`
- `openclaw/tools/voicedna_tts_hook.py`
- `openclaw/skills/audio-responder-tts/audio_tts_reply.sh`

## 1) What should change

### A. Keep VoiceDNA as the source of truth for preset selection
Use VoiceDNA’s adapter contract unchanged:
- `select_preset(agent_id, agent_name=None)`
- deterministic fallback order: `agent_id` → `agent_name` → default preset
- pilot preset set remains only:
  - `neutral`
  - `friendly`
  - `flair`

**VoiceDNA files to keep stable**
- `VoiceDNA/voicedna/openclaw_adapter.py`
- `VoiceDNA/voicedna/openclaw_live_voice.py`
- `VoiceDNA/examples/openclaw_voicedemo.py`

### B. Wire OpenClaw only at the TTS boundary
The OpenClaw integration point should stay narrow:
- `openclaw/tools/voicedna_tts_hook.py` should remain the single post-processing entry point.
- The live TTS shell path should call the hook and fall back cleanly when VoiceDNA is disabled or unavailable.
- Do **not** route unrelated core logic through VoiceDNA.

**Primary call site**
- `openclaw/skills/audio-responder-tts/audio_tts_reply.sh`

This is the safest boundary because it already owns the “generate audio / fallback to default” decision.

### C. Keep the shim lazy and opt-in
The OpenClaw shim should only instantiate VoiceDNA when enabled.
Recommended behavior:
- `VOICEDNA_OPENCLAW_PRESETS=1` is the pilot gate.
- `VOICEDNA_OPENCLAW_PRESETS_MAP` optionally overrides agent→preset mappings.
- If disabled, `get_voice_adapter()` / `render_agent_voice()` must return `None` and leave the existing TTS path unchanged.

If the existing OpenClaw branch also supports `VOICEDNA_ENABLED`, keep it only as a compatibility alias; the canonical pilot knob should remain the VoiceDNA/OpenClaw presets flag.

## 2) Exact code changes

### 2.1 `openclaw/tools/voicedna_adapter.py`
If this file is still the active shim:
- keep `get_voice_adapter()` lazy
- keep `reset_adapter()` for tests/hot reload
- load `VOICEDNA_OPENCLAW_PRESETS_MAP` as JSON
- reject invalid JSON by falling back to defaults
- preserve default map:
  - `agent:namshub` → `neutral`
  - `agent:david-hardman` → `friendly`
  - `agent:dr-voss-thorne` → `flair`

### 2.2 `openclaw/tools/voicedna_tts_hook.py`
Keep this as the canonical live hook:
- return `None` immediately when the feature flag is off
- import VoiceDNA only after the gate passes
- call `voicedna.openclaw_live_voice.render_agent_voice(...)`
- pass through:
  - `text`
  - `agent_id`
  - `agent_name` when available
  - `output_path` when the caller provided one
- if VoiceDNA returns `None`, let the current OpenClaw TTS path continue

### 2.3 `openclaw/skills/audio-responder-tts/audio_tts_reply.sh`
This is the place to wire the live TTS pipeline.
Minimal required behavior:
1. Resolve canonical `agent_id` from the short voice alias.
2. Call `tools/voicedna_tts_cli.py` first when the feature gate is on.
3. If the CLI returns failure or `None`, fall back to the existing TTS binaries.
4. Never fail the user-facing TTS flow just because VoiceDNA is absent.

### 2.4 OpenClaw tests
Add or keep unit tests around the shim and hook:
- `openclaw/tests/test_voicedna_adapter.py`
- `openclaw/tests/test_voicedna_tts_hook.py`
- `openclaw/tests/test_voicedna_e2e.py`

Coverage should prove:
- opt-in gate off → no routing
- opt-in gate on → correct preset selection
- invalid JSON map falls back safely
- synthesis-only tests skip cleanly if backend support is missing

### 2.5 Docs / operator guidance
Sync the operator docs so the implementation matches the runtime behavior:
- `openclaw/README.md`
- `openclaw/VOICEDNA_RUNBOOK.md`
- `openclaw/docs/VOICE_DNA_HANDOFF.md`
- `openclaw/docs/DESIGN_DOC_voicedna.md`

Document only the knobs that matter:
- `VOICEDNA_OPENCLAW_PRESETS`
- `VOICEDNA_OPENCLAW_PRESETS_MAP`
- optional encrypted-voice env vars, if used locally

## 3) Configuration knobs

### Required pilot env
```bash
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

### Optional local VoiceDNA env
Only if encrypted VoiceDNA artifacts are used:
- `VOICEDNA_PASSWORD_*`
- `VOICEDNA_ENC_PATH`
- `VOICEDNA_FORCE_AGE`

Do not check secrets into git.

## 4) Rollout plan

1. **Keep the feature off by default.**
2. **Confirm the adapter resolves presets correctly** using the three pilot agents.
3. **Smoke test the demo** and validate the generated WAVs.
4. **Wire the live hook at the TTS boundary** only.
5. **Enable for a small pilot group** by setting `VOICEDNA_OPENCLAW_PRESETS=1` in a controlled environment.
6. **Monitor for fallback behavior**: when VoiceDNA is unavailable, OpenClaw should behave exactly as before.
7. **Expand only after no regressions are observed** in default TTS.

## 5) Rollback plan

Rollback should be config-only unless a hook call-site change was added:
1. unset `VOICEDNA_OPENCLAW_PRESETS`
2. unset `VOICEDNA_OPENCLAW_PRESETS_MAP`
3. remove/skip the live hook call in `audio_tts_reply.sh` if needed
4. revert any docs/tests added for the pilot

No migration, schema change, or secret rotation is required.

## 6) Cross-links for implementer

### VoiceDNA implementation references
- `VoiceDNA/voicedna/openclaw_adapter.py`
- `VoiceDNA/voicedna/openclaw_live_voice.py`
- `VoiceDNA/examples/openclaw_voicedemo.py`

### OpenClaw wiring references
- `openclaw/tools/voicedna_adapter.py`
- `openclaw/tools/voicedna_tts_hook.py`
- `openclaw/tools/voicedna_tts_cli.py`
- `openclaw/skills/audio-responder-tts/audio_tts_reply.sh`
- `openclaw/tests/test_voicedna_adapter.py`
- `openclaw/tests/test_voicedna_tts_hook.py`
- `openclaw/tests/test_voicedna_e2e.py`

### Related research artifacts found
- `VoiceDNA/research/voicedna_integration_summary.md`
- `VoiceDNA/research/implementation_checklist.md`
- `VoiceDNA/research/openclaw_integration_plan.md`
- `openclaw/docs/VOICE_DNA_HANDOFF.md`
- `openclaw/VOICEDNA_RUNBOOK.md`

## 7) Bottom line

The safest implementation is narrow and additive: keep VoiceDNA responsible for preset resolution and synthesis, and keep OpenClaw responsible for deciding when to invoke it. Wire the live hook only at the TTS boundary, guard it behind `VOICEDNA_OPENCLAW_PRESETS`, and preserve the existing fallback path exactly as-is.
