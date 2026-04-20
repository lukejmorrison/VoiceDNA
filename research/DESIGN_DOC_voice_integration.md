# VoiceDNA → OpenClaw per-agent voice integration

**Goal:** wire VoiceDNA v3.1.1 into OpenClaw as an opt-in, backwards-compatible per-agent voice layer.

## Architecture

```
OpenClaw agent ID / agent name
        ↓
OpenClaw shim: `tools/voicedna_adapter.py`
        ↓  (opt-in only: `VOICEDNA_OPENCLAW_PRESETS=1`)
VoiceDNA `voicedna.openclaw_adapter.VoiceAdapter`
        ↓
Preset registry (`neutral`, `friendly`, `flair`)
        ↓
VoiceDNA synthesis / processing
        ↓
WAV bytes or output file
```

The integration stays additive:
- if the env flag is off, OpenClaw behaves exactly as before
- no core OpenClaw code needs to change for the pilot demo
- the mapping is deterministic and local-first

## Integration points

### VoiceDNA side
- `voicedna/openclaw_adapter.py`
  - `VoiceAdapter.select_preset(agent_id, agent_name=None)`
  - `VoiceAdapter.synthesize(text, preset, output_path=None)`
  - `PRESET_REGISTRY`, `DEFAULT_PRESET`, `AGENT_PRESETS`
  - `load_presets_from_env()` for `VOICEDNA_OPENCLAW_PRESETS_MAP`
- `examples/openclaw_voicedemo.py`
  - generates the 3 demo WAVs for the pilot agents
- `tests/test_voice_adapter.py`
- `tests/test_openclaw_live_voice.py`

### OpenClaw side
- `tools/voicedna_adapter.py`
  - opt-in gate around VoiceDNA usage
  - singleton adapter construction
  - default pilot mapping for the 3 agents
- `tools/voicedna_registry.py`
  - registry helper for agent → preset wiring and env export
- `skills/voicedna-agent-voices/SKILL.md`
  - operator-facing instructions
- `skills/voice-dna-registry/registry.json`
  - persisted registry state

## API surface

### Environment variables
- `VOICEDNA_OPENCLAW_PRESETS=1`
  - enables the pilot path
- `VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral",...}'`
  - optional JSON mapping of agent IDs or aliases to presets
- `VOICEDNA_PASSWORD`, `VOICEDNA_ENC_PATH`
  - only relevant if encrypted DNA artifacts are used later

### VoiceAdapter behavior
Resolution order for presets:
1. exact `agent_id`
2. `agent_name` alias, if provided
3. `default_preset` (`neutral`)

The preset registry is intentionally tiny for the pilot:
- `neutral` — calm, clear, neutral assistant voice
- `friendly` — warm, upbeat, approachable
- `flair` — expressive, distinctive, strong personality

## Performance / operational constraints

- Keep synthesis local; do not introduce cloud dependencies for the pilot.
- Use the existing VoiceDNA backend already present in the repo.
- Preserve current WAV output shape expected by tests: RIFF, PCM, mono, 22050 Hz, 16-bit.
- Avoid expensive startup work in OpenClaw: load the adapter lazily and only when the flag is on.
- Keep the mapping small and explicit; no dynamic lookup service for pilot one.

## Test plan

### VoiceDNA repo
- `python -m pytest tests/test_voice_adapter.py -v`
- `python -m pytest tests/test_openclaw_live_voice.py -v`
- demo smoke run:
  - `VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py`

### Acceptance checks
- three WAV files are regenerated under `examples/openclaw/output/`
- files are non-empty and valid WAVs
- preset selection resolves correctly for the pilot agent IDs
- fallback behavior remains stable when an agent has no explicit mapping

## Current demo result

Re-run command:

```bash
cd /home/namshub/dev/VoiceDNA
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
```

Resulting WAVs:
- `/home/namshub/dev/VoiceDNA/examples/openclaw/output/namshub_neutral.wav` — 164,696 bytes
- `/home/namshub/dev/VoiceDNA/examples/openclaw/output/david_friendly.wav` — 211,876 bytes
- `/home/namshub/dev/VoiceDNA/examples/openclaw/output/voss_flair.wav` — 209,542 bytes

## Rollout note

This should ship as a feature-flagged pilot first. If later wired directly into live OpenClaw agent audio, keep the same adapter boundary so the core voice pipeline can swap implementations without changing agent semantics.
