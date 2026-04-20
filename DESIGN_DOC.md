# VoiceDNA → OpenClaw Per-Agent Voice Integration

**Author:** Dr Voss Thorne (via subagent)  
**Date:** 2026-04-19  
**Branch:** `feature/voicedna-openclaw-per-agent-voices`

---

## Overview

This document describes the additive, opt-in integration that wires VoiceDNA's
`VoiceAdapter` into the OpenClaw agent voice pipeline so each agent can be
mapped to a distinct voice preset at runtime.

---

## Architecture

```
OpenClaw TTS request
        │
        ▼
VOICEDNA_OPENCLAW_PRESETS=1 set?
        │
   No ──┘ (existing TTS path unchanged — backward-compat preserved)
        │
   Yes  ▼
  VoiceAdapter.select_preset(agent_id)
        │
        ▼  fallback chain:
       1. exact agent_id  →  preset name
       2. agent_name alias →  preset name
       3. DEFAULT_PRESET ("neutral")
        │
        ▼
  VoiceAdapter.synthesize(text, preset)
   └─ _SimpleLocalTTS.synthesize(text)       → raw WAV bytes
   └─ VoiceDNAProcessor.process(raw, dna)    → processed WAV bytes
        │
        ▼
   WAV bytes returned / written to output_path
```

---

## Key Modules

| File | Purpose |
|------|---------|
| `voicedna/openclaw_adapter.py` | `VoiceAdapter` class, preset registry, env-driven mapping |
| `voicedna/openclaw_live_voice.py` | `render_agent_voice()` — opt-in live pipeline hook |
| `examples/openclaw_voicedemo.py` | Demo: produces WAVs for three pilot agents |
| `examples/openclaw/voicedna_tts_hook.py` | Drop-in OpenClaw skill wrapper |
| `tests/test_voice_adapter.py` | 18 unit/smoke tests (all passing) |

---

## Pilot Presets

| Preset | Agent | Description |
|--------|-------|-------------|
| `neutral` | `agent:namshub` | Calm, clear, neutral assistant |
| `friendly` | `agent:david-hardman` | Warm, upbeat, approachable |
| `flair` | `agent:dr-voss-thorne` | Expressive, sharp, distinctive |

---

## Configuration

```bash
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

`VOICEDNA_OPENCLAW_PRESETS` is the master feature flag. When absent, all
existing OpenClaw TTS behavior is unaffected.

---

## Backward Compatibility

- No existing VoiceDNA code-path imports `openclaw_adapter` or `openclaw_live_voice`.
- `render_agent_voice()` returns `None` when the feature flag is unset.
- The `VoiceDNATTSHook` in `voicedna_tts_hook.py` is copy-paste only; it is
  not auto-loaded.
- All changes are additive. No existing module signatures were modified.

---

## Testing

```bash
cd /home/namshub/dev/VoiceDNA
pytest tests/test_voice_adapter.py -q   # 18 passed
```

Synthesis tests are guarded with `@requires_voice_dna` so CI without the
backend skips them cleanly.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-04-19 | Verified `voicedna/openclaw_adapter.py` — `VoiceAdapter` wiring complete |
| 2026-04-19 | Ran `examples/openclaw_voicedemo.py` — produced 3 WAVs in `examples/openclaw/output/` |
| 2026-04-19 | Confirmed `pytest tests/test_voice_adapter.py` — 18/18 passed |
| 2026-04-19 | Added `DESIGN_DOC.md` (this file) with architecture, config, and changelog |

---

## Handoff Note for David (Edge-Case Validation)

**David: before this lands on `main`, please confirm the following edge-case scenarios:
1. An agent whose `agent_id` is absent from both `VOICEDNA_OPENCLAW_PRESETS_MAP` and the built-in pilot map correctly falls back to the `neutral` default — verify by unsetting the map env var and calling `VoiceAdapter.select_preset("agent:unknown")`.
2. A malformed or empty `VOICEDNA_OPENCLAW_PRESETS_MAP` JSON string does not crash OpenClaw at startup — `load_presets_from_env()` must log a warning and return the empty dict.
3. `render_agent_voice()` returns `None` (not an empty bytestring) when `VOICEDNA_OPENCLAW_PRESETS` is unset, so callers can safely gate on truthiness.
4. Hot-reload: calling `reset_adapter()` between tests or config changes reinitialises the singleton cleanly — confirm no stale preset mappings carry over.
5. CI smoke job (`VOICEDNA_OPENCLAW_PRESETS=1`) passes without a real TTS backend (synthesis tests must be skipped, not errored, when `voice_dna` package is absent).**

---

## Non-Goals / Future Work

- No cloud API calls or external secrets are required for the pilot.
- RVC conversion is stubbed; a downstream stage can replace the `simple` mode.
- Additional presets should be reviewed for redistribution rights before shipping.
- A CI workflow job for synthesis tests is deferred until a headless TTS
  backend is confirmed available in the CI environment.
