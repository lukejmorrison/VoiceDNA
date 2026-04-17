# feat: per-agent voice pilot — VoiceAdapter + OpenClaw demo (3 presets)

## Summary

Introduces `voicedna/openclaw_adapter.py` — a lightweight adapter that maps OpenClaw agent identities to VoiceDNA voice presets, enabling distinct per-agent TTS voices across Namshub / Dr Voss Thorne / David Hardman personas.

## Changes

| File | Description |
|------|-------------|
| `voicedna/openclaw_adapter.py` | `VoiceAdapter` class: `select_preset()`, `synthesize()`, `load_presets_from_env()`. Ships 3 pilot presets. |
| `examples/openclaw_voicedemo.py` | Demo: generates 3 agents × 3 presets → WAV output |
| `tests/test_voice_adapter.py` | 18 unit tests (20 pass including consistency/piper, 3 skipped pending backend) |
| `docs/` | README section, CHANGELOG entry, IMPLEMENTATION_NOTE |

## Test Results

```
tests/test_voice_adapter.py      ✅ PASS
tests/test_consistency_engine.py ✅ PASS
tests/test_piper_quality.py      ✅ PASS (3 skipped — synthesis backend not installed)
20 passed, 3 skipped, 0 failed

Note: 5 other test files fail collection due to missing `cryptography` dep in CI env.
These are pre-existing failures unrelated to this PR's changes.
```

## How to verify

```bash
git checkout feature/voicedna-openclaw-per-agent-voices
python -m pytest tests/test_voice_adapter.py tests/test_consistency_engine.py -v
# With synthesis backend:
python examples/openclaw_voicedemo.py
```

## Notes

- No secrets required for tests or demo
- Synthesis skips gracefully if `voice_dna` backend is absent
- Backwards-compatible; no changes to existing presets or APIs
- `cryptography` dep failures are pre-existing in this environment, unrelated to this PR
