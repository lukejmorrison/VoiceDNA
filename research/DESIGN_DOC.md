# DESIGN_DOC.md — Wiring VoiceDNA per-agent VoiceAdapter into OpenClaw TTS

**Status:** draft / implementation guide  
**Scope:** additive, opt-in only; no default behavior changes  
**References:** see `voicedna_integration_summary.md` and `implementation_checklist.md`

## Goal
Wire VoiceDNA’s per-agent `VoiceAdapter` into the live OpenClaw TTS pipeline so an agent can speak with a deterministic preset (`neutral`, `friendly`, `flair`) while preserving the existing TTS path when VoiceDNA is disabled or unavailable.

## Exact integration point
Use the **TTS output boundary**, not heartbeat or upstream planning logic.

### Canonical hook chain in OpenClaw
1. `skills/audio-responder-tts/audio_tts_reply.sh` decides whether to synthesize a reply.
2. When opt-in is enabled, it calls `tools/voicedna_tts_cli.py`.
3. `tools/voicedna_tts_cli.py` calls `tools/voicedna_tts_hook.render_agent_voice(...)`.
4. `render_agent_voice()` delegates into the VoiceDNA repo via `voicedna.openclaw_live_voice`.
5. If VoiceDNA returns `None` or fails, the shell script falls back to the existing TTS binary.

**Decision:** this is the right boundary because it is the last step before audio generation and keeps the rest of OpenClaw unchanged.

## Required env vars
Keep the feature gated and local-first:

```bash
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

Optional only if encrypted registry voices are used:

```bash
export VOICEDNA_PASSWORD_NAMSHUB=...
```

## Fallback logic
Resolution order inside VoiceDNA:
1. exact `agent_id`
2. `agent_name` alias
3. default preset (`neutral`)

Runtime behavior:
- If `VOICEDNA_OPENCLAW_PRESETS` is unset or falsy, `render_agent_voice()` returns `None`.
- If the VoiceDNA package/backend is missing, the hook returns `None` or exits non-fatally.
- The OpenClaw shell path then uses the existing TTS provider unchanged.

This keeps the pilot additive and safe to ship behind a feature flag.

## Minimal OpenClaw code changes needed
No new dependencies.

### Core changes required
- Keep `tools/voicedna_tts_hook.py` as the single hook API.
- Ensure the live TTS call site calls `render_agent_voice()` only after text has been finalized for speech.
- Preserve existing provider fallback when the hook returns `None`.
- Keep `tools/voicedna_adapter.py` as the opt-in singleton/config shim.

### If OpenClaw core needs any further edits
Only touch the TTS boundary layer, not agent planning or heartbeat code.

Recommended touch points:
- `skills/audio-responder-tts/audio_tts_reply.sh` — caller-side fallback orchestration
- `tools/voicedna_tts_hook.py` — canonical TTS post-processor
- `tools/voicedna_adapter.py` — feature flag + preset map loader

## Testing plan
Do not run synthesis tests here; this doc only defines the path.

### VoiceDNA repo checks
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -q
python -m pytest tests/test_openclaw_live_voice.py -q
```

### Smoke demo
```bash
cd /home/namshub/dev/VoiceDNA
python examples/openclaw_voicedemo.py
```

Expected output WAVs:
- `examples/openclaw/output/namshub_neutral.wav`
- `examples/openclaw/output/david_friendly.wav`
- `examples/openclaw/output/voss_flair.wav`

### Format validation
Confirm mono / 22050 Hz / 16-bit WAV output.

## Acceptance criteria
- OpenClaw stays unchanged when the env flag is off.
- VoiceDNA activates only at the TTS boundary.
- Preset selection follows `agent_id` → `agent_name` → default.
- Existing TTS remains the fallback path.
- No secrets or new dependencies are introduced.

## Notes
- The VoiceDNA side is already implemented in `voicedna/openclaw_adapter.py` and `voicedna/openclaw_live_voice.py`.
- Keep this pilot local-first and opt-in until the boundary is proven stable.
