# VoiceDNA OpenClaw per-agent voice pilot — PR summary

## One-line summary
Add an opt-in VoiceAdapter layer that maps OpenClaw agent identities to distinct VoiceDNA presets, so Namshub, Dr Voss Thorne, and David Hardman can each speak with a stable voice without changing default VoiceDNA behavior.

## What changes
- Introduces `voicedna/openclaw_adapter.py` with deterministic preset routing:
  `agent_id` → `agent_name` → default preset.
- Ships three pilot presets only:
  `neutral`, `friendly`, `flair`.
- Adds a runnable local demo at `examples/openclaw_voicedemo.py` that writes WAV files to `examples/openclaw/output/`.
- Adds focused unit tests in `tests/test_voice_adapter.py`.
- Documents the opt-in path in `README.md` and implementation notes.

## Design notes
- The feature is additive and disabled by default.
- No existing CLI or SDK defaults are changed.
- The adapter can be used directly or via an env-based mapping:
  `VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:id":"preset"}'`.
- The demo is local-first and does not require cloud services.
- If the VoiceDNA runtime backend is unavailable, synthesis fails cleanly with an explanatory error.

## Validation status
- Targeted voice-adapter tests pass locally: `15 passed, 3 skipped`.
- Ruff and bytecode checks pass for the new files.
- Full repo pytest is currently blocked in this environment by a missing `cryptography` dependency.
- Demo execution is currently blocked in this environment by missing runtime backend packages.

## Reviewer takeaway
This is a low-risk, opt-in pilot: the code path is isolated, the preset selection is deterministic, and the rollout can be backed out without affecting the rest of VoiceDNA.
