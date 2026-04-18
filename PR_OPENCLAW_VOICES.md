# Feature: Per-Agent Voice Presets for OpenClaw

## Summary

Wire the VoiceDNA VoiceAdapter into the OpenClaw agent voice pipeline, enabling agents to use distinct voice presets (neutral, friendly, flair) based on agent identity.

## Changes

### New Modules
- **`voicedna/openclaw_adapter.py`** — VoiceAdapter class with per-agent preset selection and synthesis
- **`examples/openclaw_voicedemo.py`** — Runnable demo: 3 agents × 3 presets → WAV output
- **`tests/test_voice_adapter.py`** — 18 unit/smoke tests (preset registry, selection, synthesis, env)
- **`tests/test_openclaw_live_voice.py`** — 13 integration tests (demo, agent mapping, e2e)

### Key Features

1. **Preset Registry** — Three pilot presets (neutral, friendly, flair) with voice DNA parameters
2. **Agent Mapping** — Environment-driven (JSON) or programmatic agent ID → preset resolution
3. **Fallback Chain** — agent_id → agent_name → default_preset for robust resolution
4. **Opt-in Activation** — `VOICEDNA_OPENCLAW_PRESETS=1` signals production readiness; feature is isolated
5. **No Breaking Changes** — Existing VoiceDNA CLI/SDK behavior unchanged; feature is additive

### Testing

- ✅ 31 tests pass (18 unit + 13 integration)
- ✅ Linting passes (ruff all-clear)
- ✅ Demo produces 3 valid WAV files (164–211 KB each)
- ✅ End-to-end synthesis pipeline validated

### Example Usage

```python
from voicedna.openclaw_adapter import VoiceAdapter

adapter = VoiceAdapter(agent_presets={
    "agent:namshub": "neutral",
    "agent:dr-voss-thorne": "flair",
})

preset = adapter.select_preset("agent:namshub")
wav = adapter.synthesize("Hello.", preset, output_path="output.wav")
```

### Configuration

```bash
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:dr-voss-thorne":"flair"}'
export VOICEDNA_OPENCLAW_PRESETS=1
```

## Validation

- Preset registry: complete, validated
- Agent ID handling: full OpenClaw format (agent:namespace:id)
- Synthesis: end-to-end tested, output verified (RIFF/WAVE format)
- Code quality: linted, tested, documented

## Artifacts

- Branch: `feature/voicedna-openclaw-per-agent-voices`
- Demo WAVs: `/examples/openclaw/output/`
- Test logs: 31/31 passed in 1.71s
- Verification report: `VERIFICATION_REPORT.md`
