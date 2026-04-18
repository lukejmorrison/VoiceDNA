# feat: per-agent voice pilot — VoiceAdapter + OpenClaw demo (3 presets)

## Summary

Introduces `voicedna/openclaw_adapter.py` — a lightweight, opt-in adapter that maps OpenClaw agent identities to VoiceDNA voice presets, enabling distinct per-agent TTS voices across the Namshub / Dr Voss Thorne / David Hardman personas without changing default VoiceDNA behavior.

## Release notes

- Adds deterministic per-agent voice routing: `agent_id` → `agent_name` → default preset.
- Ships three pilot presets only: `neutral`, `friendly`, `flair`.
- Adds a local demo that writes WAV output under `examples/openclaw/output/`.
- Keeps the feature additive and disabled by default.
- Documentation and tests are updated to cover the pilot flow and expected usage.

## Changes

| File | Description |
|------|-------------|
| `voicedna/openclaw_adapter.py` | `VoiceAdapter` class: `select_preset()`, `synthesize()`, `load_presets_from_env()`, plus runtime registration helpers. Ships 3 pilot presets. |
| `examples/openclaw_voicedemo.py` | Demo: generates 3 agents × 3 presets → WAV output |
| `tests/test_voice_adapter.py` | Focused unit/smoke coverage for preset selection, env loading, and synthesis guards |
| `README.md` / `CHANGELOG.md` / `IMPLEMENTATION_NOTE.md` / `research/voicedna_integration_summary.md` / `research/implementation_checklist.md` | User-facing docs, rollout notes, and review prep packet |

## Test Results

```
python -m pytest tests/test_voice_adapter.py -v   ✅ 15 passed, 3 skipped
ruff check voicedna/openclaw_adapter.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py   ✅ PASS
python -m py_compile voicedna/openclaw_adapter.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py   ✅ PASS
python -m pytest -q   ⛔ blocked in this environment by missing cryptography
python examples/openclaw_voicedemo.py   ⛔ blocked in this environment by missing runtime backend deps
```

## How to verify

```bash
git checkout feature/voicedna-openclaw-per-agent-voices
python -m pytest tests/test_voice_adapter.py -v
ruff check voicedna/openclaw_adapter.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py
python examples/openclaw_voicedemo.py  # only in an environment with the VoiceDNA runtime backend
```

## PR checklist

- [x] Confirm the three pilot presets exist: `neutral`, `friendly`, `flair`
- [x] Confirm routing order is deterministic: `agent_id` → `agent_name` → default
- [x] Confirm the demo maps the three personas to three different presets
- [x] Confirm the adapter is opt-in and does not alter default VoiceDNA behavior
- [x] Confirm targeted tests, lint, and bytecode checks pass locally
- [ ] Re-run the full repo test suite in a dependency-complete environment
- [ ] Re-run the demo where the VoiceDNA runtime backend stack is installed
- [ ] Verify no unintended files are included in the PR
- [ ] Obtain reviewer sign-off from Namshub and Dr Voss Thorne

## Workflow / permissions note

- This branch does **not** change any `.github/workflows/*` files relative to `origin/main`.
- For the current diff, a normal repo push should only need standard source write access (`contents:write`) and PR creation/update access (`pull_requests:write`) if using a PAT or API-backed push flow.
- If a future revision adds or edits workflow files, the token must also include **`workflow` scope**.
- `workflow` is required because GitHub treats workflow-file changes as privileged repository actions and may reject pushes or updates without that permission.

## Notes

- No secrets required for tests or demo.
- Synthesis skips gracefully if the `voice_dna` backend is absent.
- Backwards-compatible; no changes to existing presets or APIs.
- The repository-wide pytest failure observed here is an environment dependency issue, not a pilot regression.
