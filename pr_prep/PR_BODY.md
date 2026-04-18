# feat: per-agent voice pilot — VoiceAdapter + OpenClaw demo (3 presets)

## Summary

Introduces `voicedna/openclaw_adapter.py` — a lightweight, opt-in adapter that maps OpenClaw agent identities to VoiceDNA voice presets, enabling distinct per-agent TTS voices across the Namshub / Dr Voss Thorne / David Hardman personas without changing default VoiceDNA behavior.

## Release Notes

- Adds deterministic per-agent voice routing: `agent_id` → `agent_name` → default preset.
- Ships three pilot presets only: `neutral`, `friendly`, `flair`.
- Adds a local demo that writes WAV output under `examples/openclaw/output/`.
- Keeps the feature additive and disabled by default.
- Documentation and tests cover the pilot flow and expected usage.

## Changes

| File | Description |
|------|-------------|
| `voicedna/openclaw_adapter.py` | `VoiceAdapter` class: `select_preset()`, `synthesize()`, `load_presets_from_env()`, plus runtime registration helpers. Ships 3 pilot presets. |
| `examples/openclaw_voicedemo.py` | Demo: generates 3 agents × 3 presets → WAV output |
| `tests/test_voice_adapter.py` | Unit/smoke coverage for preset selection, env loading, and synthesis guards |
| `README.md` / `CHANGELOG.md` / `IMPLEMENTATION_NOTE.md` | User-facing docs and rollout notes |
| `research/voicedna_integration_summary.md` / `research/implementation_checklist.md` | Review prep packet |

## Test Results (2026-04-17)

```
python -m pytest -q            ✅ 34 passed in 1.57s
ruff check .                   ✅ All checks passed
```

Full suite clean. No failures. No lint errors.

## How to Verify

```bash
git checkout feature/voicedna-openclaw-per-agent-voices
python -m pytest -q
ruff check .
python examples/openclaw_voicedemo.py  # requires VoiceDNA runtime backend
```

## Reviewers
- **Dr Voss Thorne** — architecture, adapter design, test coverage
- **Luke Morrison** — product direction, release sign-off
