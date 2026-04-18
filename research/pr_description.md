# Draft PR description — OpenClaw live VoiceDNA per-agent voices

**Target repo:** `openclaw`
**Target branch:** `feat/voicedna-openclaw-integration`
**VoiceDNA release anchor:** `v3.1.1` (`69d8d0c`)

## Title

**feat: opt-in VoiceDNA per-agent voices for OpenClaw**

## Body

```md
## Summary

This PR wires VoiceDNA v3.1.1’s `VoiceAdapter` into the live OpenClaw agent voice pipeline behind a strict opt-in gate.

When `VOICEDNA_OPENCLAW_PRESETS=1` is set, OpenClaw routes agent speech through VoiceDNA preset selection so each known agent can keep a stable voice profile:

- `agent:namshub` → `neutral`
- `agent:david-hardman` → `friendly`
- `agent:dr-voss-thorne` → `flair`

Default behavior is unchanged when the flag is absent.

## What changed

- Adds/uses a lightweight OpenClaw shim for VoiceDNA preset routing.
- Wires the live TTS seam so it calls `render_agent_voice(...)` only when the feature flag is enabled.
- Keeps the preset map in `VOICEDNA_OPENCLAW_PRESETS_MAP` as JSON.
- Preserves the current TTS path as the fallback.
- Adds/updates tests for the live seam and the OpenClaw-side adapter.
- Keeps the rollout local-first and reversible.

## Files of interest

- `skills/audio-responder-tts/audio_tts_reply.sh`
- `tools/voicedna_adapter.py`
- `skills/audio-responder-tts/SKILL.md`
- `VOICEDNA_RUNBOOK.md`
- `tests/test_voicedna_adapter.py`

## Validation

VoiceDNA side:

- `python -m pytest tests/test_voice_adapter.py -v`
- `python -m pytest tests/test_openclaw_live_voice.py -v`
- `python -m pytest -q`
- `ruff check voicedna/openclaw_adapter.py voicedna/openclaw_live_voice.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py tests/test_openclaw_live_voice.py`
- `python -m py_compile voicedna/openclaw_adapter.py voicedna/openclaw_live_voice.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py tests/test_openclaw_live_voice.py`
- `VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py`

OpenClaw side:

- `python -m pytest tests/test_voicedna_adapter.py -v`
- `ruff check tools/voicedna_adapter.py tests/test_voicedna_adapter.py`
- `python -m py_compile tools/voicedna_adapter.py tests/test_voicedna_adapter.py`

## Rollout

1. Set `VOICEDNA_OPENCLAW_PRESETS=1` in the active OpenClaw env file.
2. Optionally set `VOICEDNA_OPENCLAW_PRESETS_MAP` with the pilot mapping JSON.
3. Restart the OpenClaw user service.
4. Smoke-test the live TTS path and confirm the WAV outputs are non-empty.

## Rollback

1. Unset `VOICEDNA_OPENCLAW_PRESETS` and `VOICEDNA_OPENCLAW_PRESETS_MAP`.
2. Restart the OpenClaw service.
3. Revert the live seam hook if needed.
4. Confirm the original TTS path works unchanged.

## CI / merge notes

- No `.github/workflows/*` files are changed in this rollout.
- No workflow-file permission uplift is required unless a future revision touches Actions YAML.
- The minimum token scopes for a token-based push/PR flow are `contents:write` and `pull_requests:write`.

## Approvals / secrets

No deploy key or service-account secret is required for the preset-routing pilot. If a future revision touches workflow files, the token will also need `workflow` scope.
```

## Reviewer checklist

- [ ] Feature is still opt-in and does not alter default TTS behavior
- [ ] `VOICEDNA_OPENCLAW_PRESETS_MAP` remains the only routing config path
- [ ] No workflow files are included in the diff
- [ ] Rollback is simple: unset env vars and restart
- [ ] Demo/test evidence is attached or linked
```