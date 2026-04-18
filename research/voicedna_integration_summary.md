# VoiceDNA → OpenClaw Per-Agent Voice Pilot Summary

Scope: VoiceDNA repo + OpenClaw example integration for per-agent voices.

## What exists now
- `DESIGN_DOC.md` defines the pilot: a small `VoiceAdapter` layer, an OpenClaw demo at `examples/openclaw_voicedemo.py`, 3 presets (`neutral`, `friendly`, `flair`), and smoke/unit tests.
- I did **not** find any additional VoiceDNA source files, example scripts, or tests in the current workspace beyond `DESIGN_DOC.md`.

## Required code changes
1. Add a programmatic adapter API in VoiceDNA, likely `voice_adapter.py`, exposing:
   - `select_preset(agent_id | agent_name)`
   - `synthesize(text, preset)`
   - optional helper for config lookup / defaults
2. Add an OpenClaw example script, likely `examples/openclaw_voicedemo.py`, that:
   - loads a per-agent mapping (`agent_id -> preset`)
   - calls `VoiceAdapter` for speech output
   - shows 3 agents using distinct presets
3. Add tests, likely under `tests/`, covering:
   - preset selection logic
   - fallback/default preset behavior
   - audio generation / non-empty output smoke case
4. Add minimal docs/usage notes and an opt-in config surface so public VoiceDNA CLI/SDK behavior stays unchanged.

## Compatibility notes
- Keep the feature behind opt-in config to avoid breaking existing VoiceDNA semantics.
- Preserve current preset names and SDK/CLI behavior; add the adapter as an additive layer.
- Verify the adapter works with whatever VoiceDNA version is pinned in the repo/published package (`v2.9.7` per design doc).
- Ensure the demo does not require cloud infrastructure; local execution is preferred.

## Config options to support
- `agent_id -> preset` mapping file or dict
- default preset fallback
- optional agent-name lookup aliasing
- per-agent override precedence: explicit mapping > named alias > default

## Blockers / gaps
- The workspace currently lacks the underlying VoiceDNA source tree, examples, tests, README, and packaging files needed to confirm exact integration points.
- License/preset compatibility is unresolved until the actual VoiceDNA preset assets and license terms are inspected.
- CI/test harness specifics are unknown.

## Exact files expected to change
- `voice_adapter.py` (new)
- `examples/openclaw_voicedemo.py` (new)
- `tests/test_voice_adapter.py` or similar (new)
- `tests/test_openclaw_voicedemo.py` or similar (new)
- `README.md` and/or usage docs if present
- `pyproject.toml` if new deps or test markers are needed
