# PR: Wire VoiceDNA per-agent VoiceAdapter into OpenClaw

## Summary
This PR keeps VoiceDNA’s per-agent voice routing additive and opt-in while wiring the live OpenClaw voice seam to use the existing `VoiceAdapter` contract. The default OpenClaw TTS path remains unchanged unless `VOICEDNA_OPENCLAW_PRESETS=1` is set.

## What’s included
- Opt-in preset routing via `tools/voicedna_adapter.py`
- Canonical live seam via `tools/voicedna_tts_hook.py`
- Preset selection order: `agent_id` → `agent_name` → default
- Pilot presets: `neutral`, `friendly`, `flair`
- Unit and smoke tests for shim behavior and synthesis output
- Docs sync for runtime usage and rollback

## File targets
- `tools/voicedna_adapter.py`
- `tools/voicedna_tts_hook.py`
- `tests/test_voicedna_adapter.py`
- `tests/test_voicedna_e2e.py`
- `skills/audio-responder-tts/audio_tts_reply.sh` if agent identity must be passed through
- `skills/audio-responder-tts/SKILL.md` for docs after the seam is proven

## Validation
- `python -m pytest tests/test_voicedna_adapter.py -v`
- `python -m pytest tests/test_voicedna_e2e.py -v`
- `python -m pytest tests/test_voicedna_tts_hook.py -v`
- `VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py`

## Rollback
Unset `VOICEDNA_OPENCLAW_PRESETS` and `VOICEDNA_OPENCLAW_PRESETS_MAP`, then revert the narrow live seam patch if needed. Default OpenClaw behavior stays intact.

## Notes for reviewers
- Keep this change additive and opt-in.
- Do not change public CLI/SDK defaults.
- Flag any packaging/import-path assumptions that depend on a local checkout rather than an installed package.
