# OpenClaw ↔ VoiceDNA Implementation Checklist

## Objective
Implement the smallest safe wiring so OpenClaw can route per-agent speech through VoiceDNA without changing default behavior.

## Repository paths
- VoiceDNA repo: `/home/namshub/dev/VoiceDNA`
- OpenClaw repo: `/home/namshub/dev/openclaw`

## 0) Pre-flight
- [ ] Confirm branches and clean status in both repos
  - `cd /home/namshub/dev/VoiceDNA && git status --short --branch && git branch --show-current`
  - `cd /home/namshub/dev/openclaw && git status --short --branch && git branch --show-current`
- [ ] Verify the pilot VoiceDNA files still exist
  - `voicedna/openclaw_adapter.py`
  - `voicedna/openclaw_live_voice.py`
  - `examples/openclaw_voicedemo.py`
- [ ] Verify the OpenClaw shim/hook files still exist
  - `tools/voicedna_adapter.py`
  - `tools/voicedna_tts_hook.py`
  - `tools/voicedna_tts_cli.py`
  - `skills/audio-responder-tts/audio_tts_reply.sh`

## 1) Lock the feature gate
- [ ] Keep the pilot behind `VOICEDNA_OPENCLAW_PRESETS=1`
- [ ] Preserve `VOICEDNA_OPENCLAW_PRESETS_MAP` as the optional JSON mapping override
- [ ] If `VOICEDNA_ENABLED` is supported in the branch, keep it only as a compatibility alias
- [ ] Ensure the disabled path returns `None` and does not alter the current TTS flow

## 2) Preserve VoiceDNA adapter contract
- [ ] Keep `select_preset(agent_id, agent_name=None)` fallback order:
  1. `agent_id`
  2. `agent_name`
  3. default preset
- [ ] Keep the pilot preset set limited to:
  - `neutral`
  - `friendly`
  - `flair`
- [ ] Confirm invalid preset names fail safely or skip with a warning, but do not expand the supported set
- [ ] Keep `examples/openclaw_voicedemo.py` as the smoke-test script

## 3) OpenClaw wiring changes
- [ ] Wire the live TTS call at the narrowest boundary only
- [ ] In `skills/audio-responder-tts/audio_tts_reply.sh`, call VoiceDNA first when the feature flag is active
- [ ] Map short voice names to canonical agent IDs before the VoiceDNA call
  - `namshub` → `agent:namshub`
  - `voss` / `dr-voss-thorne` → `agent:dr-voss-thorne`
  - `david-hardman` → `agent:david-hardman`
- [ ] Fall back to the existing TTS binaries when VoiceDNA is disabled or returns empty/failed output
- [ ] Do not change unrelated OpenClaw core paths

## 4) Test coverage
- [ ] Add/keep unit tests for the shim gate
  - `tests/test_voicedna_adapter.py`
- [ ] Add/keep unit tests for the live hook
  - `tests/test_voicedna_tts_hook.py`
- [ ] Add/keep end-to-end tests that skip synthesis cleanly if the backend is absent
  - `tests/test_voicedna_e2e.py`
- [ ] Assert feature flag off means no routing
- [ ] Assert feature flag on resolves the correct preset for the pilot agents
- [ ] Assert invalid JSON in `VOICEDNA_OPENCLAW_PRESETS_MAP` falls back safely
- [ ] Assert demo WAVs are valid RIFF/WAVE files when synthesis is available

## 5) Demo and smoke-test
- [ ] Run VoiceDNA unit tests
  - `cd /home/namshub/dev/VoiceDNA && python -m pytest tests/test_voice_adapter.py tests/test_openclaw_live_voice.py -q`
- [ ] Run the VoiceDNA demo
  - `cd /home/namshub/dev/VoiceDNA && VOICEDNA_OPENCLAW_PRESETS=1 python examples/openclaw_voicedemo.py`
- [ ] Validate the output files exist and are non-empty
  - `examples/openclaw/output/namshub_neutral.wav`
  - `examples/openclaw/output/david_friendly.wav`
  - `examples/openclaw/output/voss_flair.wav`
- [ ] Confirm OpenClaw can invoke the hook and still fall back when VoiceDNA is off

## 6) Documentation sync
- [ ] Update OpenClaw operator docs only if runtime behavior changes
  - `README.md`
  - `VOICEDNA_RUNBOOK.md`
  - `docs/VOICE_DNA_HANDOFF.md`
  - `docs/DESIGN_DOC_voicedna.md`
- [ ] Keep the docs aligned to the actual env vars used in code
- [ ] Do not add secret values to docs or git

## 7) Rollout
- [ ] Merge the wiring as an additive change
- [ ] Enable the feature for a small pilot only
- [ ] Verify no regressions in default TTS behavior
- [ ] Expand rollout only after the fallback path is confirmed stable

## 8) Rollback
- [ ] Unset `VOICEDNA_OPENCLAW_PRESETS`
- [ ] Unset `VOICEDNA_OPENCLAW_PRESETS_MAP`
- [ ] Revert the hook call-site change if one was added
- [ ] Leave VoiceDNA core untouched

## 9) Deliverables to hand off to Dr Voss
- [ ] `VoiceDNA/research/openclaw_voice_integration_plan.md`
- [ ] `VoiceDNA/research/openclaw_voice_implementation_checklist.md`
- [ ] Relevant existing reference docs listed in the plan
- [ ] Clear file-path cross-links to OpenClaw wiring points

## 10) Acceptance criteria
- [ ] Default behavior unchanged when feature flag is off
- [ ] Pilot agents resolve to neutral/friendly/flair as documented
- [ ] Demo emits 3 valid WAV files
- [ ] Unit tests pass or skip cleanly when backend support is unavailable
- [ ] Rollback is configuration-only unless the hook call-site was modified
