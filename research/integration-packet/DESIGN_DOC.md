# VoiceDNA → OpenClaw per-agent voice pilot

**Branch:** `feature/voicedna-openclaw-per-agent-voices`  
**Release anchor:** VoiceDNA `v3.1.1` (`69d8d0c`)  
**Scope:** opt-in, additive, local-first per-agent voice routing

## Purpose
Wire VoiceDNA’s `VoiceAdapter` into the OpenClaw agent voice path so specific agents can speak with stable presets without changing default VoiceDNA behavior.

## Approach
- Use `voicedna.openclaw_live_voice.render_agent_voice(...)` as the integration seam.
- Keep routing deterministic: `agent_id` → `agent_name` → default preset.
- Limit the pilot to three presets only: `neutral`, `friendly`, `flair`.
- Make activation explicit with `VOICEDNA_OPENCLAW_PRESETS=1` and optional `VOICEDNA_OPENCLAW_PRESETS_MAP`.
- Preserve current behavior when the env flag is absent.

## Recommended OpenClaw seam
- Current live TTS path: `/home/namshub/dev/openclaw/skills/audio-responder-tts/audio_tts_reply.sh`
- Helper shim already exists in OpenClaw: `/home/namshub/dev/openclaw/tools/voicedna_adapter.py`
- VoiceDNA entry point: `/home/namshub/dev/VoiceDNA/voicedna/openclaw_live_voice.py`

## Tradeoffs
- **Pros:** low risk, opt-in, no default behavior change, easy rollback.
- **Cons:** depends on local VoiceDNA runtime backend for actual synthesis; live wiring still needs a small OpenClaw-side hook.
- **Rollback:** unset env vars and remove the seam import/hook; no core VoiceDNA changes are required.

## Validation status
- VoiceDNA `v3.1.1` and branch `feature/voicedna-openclaw-per-agent-voices` both exist.
- Adapter tests and demo outputs are already documented in `research/`.
- Demo WAVs are present under `examples/openclaw/output/`.
