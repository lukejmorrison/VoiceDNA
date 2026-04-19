# VoiceDNA → OpenClaw research summary

Date: 2026-04-19

## Goal
Enable Dr Voss Thorne to wire VoiceDNA into OpenClaw without changing default behavior.

## What is already in place
The VoiceDNA side already has the per-agent voice pilot implemented and tested locally:

- `voicedna/openclaw_adapter.py` — core preset registry + routing/synthesis API
- `voicedna/openclaw_live_voice.py` — opt-in live bridge that returns `None` unless `VOICEDNA_OPENCLAW_PRESETS=1`
- `examples/openclaw_voicedemo.py` — local demo that writes three WAV files
- `tests/test_voice_adapter.py` — preset selection, env parsing, and synthesis smoke tests
- `tests/test_openclaw_live_voice.py` — opt-in guard and end-to-end bridge tests

Supporting docs already exist and are consistent with the current pilot:
- `README.md` — OpenClaw pilot section, env vars, and demo command
- `research/voicedna_integration_summary.md` — compact integration status note
- `research/implementation_checklist.md` — basic validation checklist
- `research/openclaw_integration_prep.md` and `research/voicedna_openclaw_integration_checklist.md` — deeper handoff notes

## Exact files worth keeping in scope
### Primary VoiceDNA implementation surface
- `voicedna/openclaw_adapter.py`
  - `VoiceAdapter.select_preset(agent_id, agent_name=None)`
  - `VoiceAdapter.synthesize(text, preset, output_path=None)`
  - `load_presets_from_env()` for `VOICEDNA_OPENCLAW_PRESETS_MAP`
- `voicedna/openclaw_live_voice.py`
  - `render_agent_voice(...)` live seam
  - `reset_adapter()` for tests/hot reload
- `examples/openclaw_voicedemo.py`
  - writes `namshub_neutral.wav`, `david_friendly.wav`, `voss_flair.wav`
- `tests/test_voice_adapter.py`
  - deterministic preset routing and synthesis smoke coverage
- `tests/test_openclaw_live_voice.py`
  - opt-in guard, alias fallback, and e2e checks

### Older / reference hook examples in the repo
- `examples/openclaw/voicedna_tts_hook.py`
- `examples/openclaw_hook.py`
- `examples/openclaw_skill.py`

These are useful references for a TTS-boundary hook, but the current pilot is anchored on `voicedna/openclaw_live_voice.py` and `voicedna/openclaw_adapter.py`.

## Integration contract
The intended runtime behavior is:
1. OpenClaw passes `text`, `agent_id`, and optionally `agent_name` to the VoiceDNA bridge.
2. VoiceDNA resolves a preset in this order:
   - exact `agent_id`
   - exact `agent_name` alias
   - default preset (`neutral`)
3. If `VOICEDNA_OPENCLAW_PRESETS` is unset, the bridge returns `None` and OpenClaw keeps its normal TTS path.
4. If enabled, VoiceDNA returns WAV bytes and may also write an output file.

## Current env surface
- `VOICEDNA_OPENCLAW_PRESETS=1`
- `VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'`
- `VOICEDNA_ENC_PATH` for encrypted VoiceDNA location
- `VOICEDNA_PASSWORD` for decrypting the VoiceDNA file
- `VOICEDNA_FORCE_AGE` for optional age override during processing

## Main blockers to watch
- **GitHub push/PR blocker:** a PAT may be required if the branch must be pushed from this host.
  - Remediation: prefer bundle handoff or user-side push first; only use a PAT if Luke explicitly approves it.
- **External backend blocker:** some non-local TTS backends require their own API keys or model files.
  - Remediation: keep the pilot local-first; only enable cloud/natural backends when the relevant key/model is already available.
- **OpenClaw live seam blocker:** the final runtime hook must be placed where agent identity is already known.
  - Remediation: patch only the narrowest TTS call site; do not refactor broad voice paths.

## Recommended next move
Give Dr Voss the `DESIGN_DOC.md` plus the top-5 checklist in `prep_for_voss/checklist.md`, then have him wire the narrow OpenClaw TTS seam and run the local validation commands before any push.