# Release Notes — VoiceDNA per-agent voice pilot

This pilot adds an opt-in OpenClaw voice routing layer that gives each agent a distinct VoiceDNA preset without changing default VoiceDNA behavior. The adapter resolves voices deterministically by `agent_id` → `agent_name` → default preset, and the pilot ships only three presets: `neutral`, `friendly`, and `flair`. A local demo is included to generate WAV output for the three personas under `examples/openclaw/output/`.

- **What changed:** Added `voicedna/openclaw_adapter.py`, OpenClaw demo wiring, and targeted tests for preset selection, env loading, runtime registration, and synthesis paths.
- **How to test:** Run `python -m pytest tests/test_voice_adapter.py -v` and, in a dependency-complete environment, `python examples/openclaw_voicedemo.py`; confirm the three WAV outputs are created and non-empty.
- **Notable risks:** Full repo verification depends on the local VoiceDNA runtime stack (`voice_dna`/`cryptography` in this workspace); demo synthesis is intentionally skipped if the backend is missing, and generated WAV artifacts should be reviewed before commit.
