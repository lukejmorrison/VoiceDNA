# Feature: Per-Agent Voice Presets for OpenClaw

## Summary

Wire the VoiceDNA `VoiceAdapter` into the OpenClaw agent voice pipeline, enabling agents to use distinct voice presets (`neutral`, `friendly`, `flair`) based on agent identity. Fully opt-in via env vars — default VoiceDNA behavior is unchanged.

## Branch

`feature/voicedna-openclaw-per-agent-voices`

## Changes

### New Modules
| File | Purpose |
|------|---------|
| `voicedna/openclaw_adapter.py` | `VoiceAdapter` class: per-agent preset selection + synthesis |
| `voicedna/openclaw_live_voice.py` | `render_agent_voice()` — OpenClaw TTS hook entry point |
| `examples/openclaw_voicedemo.py` | Demo: 3 agents × 3 presets → WAV output |
| `tests/test_voice_adapter.py` | Unit/smoke tests for VoiceAdapter |
| `tests/test_openclaw_live_voice.py` | Integration tests: demo, agent mapping, live bridge |

### Key Features

1. **Preset Registry** — Three pilot presets (`neutral`, `friendly`, `flair`) with voice DNA parameters
2. **Agent Mapping** — Environment-driven (JSON) or programmatic `agent_id → preset` resolution
3. **Fallback Chain** — `agent_id` → `agent_name` → `default_preset`
4. **Opt-in Activation** — `VOICEDNA_OPENCLAW_PRESETS=1` activates the hook; absent = no-op
5. **No Breaking Changes** — Existing VoiceDNA CLI/SDK behavior is unchanged

## Test Instructions

```bash
cd /path/to/VoiceDNA

# Unit + integration tests
python -m pytest tests/test_voice_adapter.py tests/test_openclaw_live_voice.py -q

# Full suite
python -m pytest -q

# Demo smoke test (produces 3 WAV files)
python -m examples.openclaw_voicedemo
```

## Expected Outputs

| File | Description |
|------|-------------|
| `examples/openclaw/output/namshub_neutral.wav` | Namshub — neutral preset |
| `examples/openclaw/output/david_friendly.wav` | David Hardman — friendly preset |
| `examples/openclaw/output/voss_flair.wav` | Dr Voss Thorne — flair preset |

All three files should be non-empty RIFF/WAVE format (≥ 100 KB each at 22050 Hz 16-bit mono).

## Configuration

```bash
# Production opt-in
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

## Programmatic Usage

```python
from voicedna.openclaw_live_voice import render_agent_voice

wav_bytes = render_agent_voice(
    text=tts_text,
    agent_id=agent.id,
    agent_name=getattr(agent, "name", None),
    output_path=maybe_output_path,
)
# returns None when VOICEDNA_OPENCLAW_PRESETS is not set (no-op)
```

Or use the adapter directly:

```python
from voicedna.openclaw_adapter import VoiceAdapter

adapter = VoiceAdapter(agent_presets={
    "agent:namshub": "neutral",
    "agent:dr-voss-thorne": "flair",
})
preset = adapter.select_preset("agent:namshub")
wav = adapter.synthesize("Hello.", preset, output_path="output.wav")
```

## Rollback

1. Unset `VOICEDNA_OPENCLAW_PRESETS` and `VOICEDNA_OPENCLAW_PRESETS_MAP`
2. Remove the `render_agent_voice()` import from the OpenClaw hook
3. Return to the previous TTS path

No schema migration or persistent state required.

## Validation Results

- ✅ 52 tests pass (31 unit + 21 integration)
- ✅ Demo produces 3 valid WAV files (164–212 KB each)
- ✅ WAVs are valid RIFF PCM 16-bit mono 22050 Hz
- ✅ `VOICEDNA_OPENCLAW_PRESETS` guard confirmed: returns `None` when unset
- ✅ Linting passes (ruff)
- ✅ No changes to existing VoiceDNA public API
