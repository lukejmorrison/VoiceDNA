# VoiceDNA OpenClaw per-agent voice pilot — Implementation Checklist

**Branch:** `feature/voicedna-openclaw-per-agent-voices`

## Scope check
- [x] `VoiceAdapter` exists in `voicedna/openclaw_adapter.py`
- [x] Preset routing is deterministic: `agent_id` → `agent_name` → default
- [x] Pilot presets are limited to `neutral`, `friendly`, and `flair`
- [x] Feature is opt-in and does not change default VoiceDNA behavior
- [x] Demo script writes WAV output under `examples/openclaw/output/`
- [x] Tests cover preset selection, env loading, registration, and synth paths

## Pre-push verification
- [ ] Run `python -m pytest tests/test_voice_adapter.py -v`
- [ ] Run `python -m pytest` in a dependency-complete environment
- [ ] Run `ruff check voicedna/openclaw_adapter.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py`
- [ ] Run `python -m py_compile voicedna/openclaw_adapter.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py`
- [ ] Run `python examples/openclaw_voicedemo.py` in an environment with the VoiceDNA runtime backend installed
- [ ] Confirm demo WAVs are present and non-empty
- [ ] Confirm no unintended files are included in the PR

## PR content checks
- [ ] PR body matches the actual preset names in code: `neutral`, `friendly`, `flair`
- [ ] PR body reflects the reported test outcomes accurately
- [ ] PR checklist includes rollout and rollback notes
- [ ] Release notes mention the demo, the opt-in behavior, and the deterministic routing order
- [ ] Any mention of workflow permissions is limited to future workflow-file changes only

## Manual QA steps
- [ ] Verify `agent:namshub` resolves to `neutral`
- [ ] Verify `agent:david-hardman` resolves to `friendly`
- [ ] Verify `agent:dr-voss-thorne` resolves to `flair`
- [ ] Verify unknown agent ids fall back to the default preset
- [ ] Verify invalid preset names fail clearly
- [ ] Verify the demo output files exist:
  - [ ] `examples/openclaw/output/namshub_neutral.wav`
  - [ ] `examples/openclaw/output/david_friendly.wav`
  - [ ] `examples/openclaw/output/voss_flair.wav`

## Rollout / rollback
- [ ] Keep the feature disabled by default unless explicitly opted in
- [ ] Avoid wiring the adapter into broader OpenClaw paths until the pilot is approved
- [ ] Revert the adapter/demo/test/docs files to roll back the pilot

## Blockers to clear before approval
- [ ] Re-run or confirm the full repo test suite in a dependency-complete environment
- [ ] Confirm the local VoiceDNA runtime backend is installed for demo synthesis
- [ ] Clean the working tree of any stray generated files before pushing
