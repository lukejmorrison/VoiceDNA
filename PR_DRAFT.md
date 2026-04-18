## Per-agent OpenClaw voice presets

**Branch:** `feature/voicedna-openclaw-per-agent-voices`  
**Base:** `main`

### Summary

Introduces `voicedna/openclaw_adapter.py` — a lightweight adapter that maps OpenClaw agent identities to VoiceDNA voice presets, enabling per-agent TTS voices across the Namshub/Dr Voss Thorne/David Hardman personas.

### Changes

- **`voicedna/openclaw_adapter.py`** — `VoiceAdapter` class with `select_preset()`, `synthesize()`, `load_presets_from_env()`, and runtime registration helpers. Ships 3 pilot presets (`neutral`, `friendly`, `flair`).
- **`examples/openclaw_voicedemo.py`** — Demo: generates 3 agents × 3 presets → WAV files in `examples/openclaw/output/`.
- **`tests/test_voice_adapter.py`** — focused unit/smoke coverage for preset selection, env loading, runtime registration, and synthesis paths (targeted run: 15 passed, 3 skipped).
- **`README.md` / `CHANGELOG.md` / `IMPLEMENTATION_NOTE.md`** — user-facing docs and rollout notes.

### Test Results

```
15 passed, 3 skipped (synthesis backend not installed — intentional)
0 failures
```

### How to verify locally

```bash
git checkout feature/voicedna-openclaw-per-agent-voices
python -m pytest tests/test_voice_adapter.py tests/test_consistency_engine.py -v
# Optionally, with synthesis backend:
python examples/openclaw_voicedemo.py
```

### Notes

- No secrets required for tests or demo.
- Synthesis skips gracefully if `voice_dna` backend is absent.
- Backwards-compatible; no changes to existing presets or APIs.
