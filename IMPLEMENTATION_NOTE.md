# IMPLEMENTATION_NOTE.md — VoiceDNA per-agent voice pilot

Branch: `feature/voicedna-openclaw-per-agent-voices`
Author: Dr Voss Thorne (subagent)
Date: 2026-04-13

---

## What was implemented

| File | Purpose |
|------|---------|
| `voicedna/openclaw_adapter.py` | New `VoiceAdapter` class — opt-in per-agent voice routing |
| `examples/openclaw_voicedemo.py` | Runnable demo: 3 agents × 3 presets → 3 WAV files |
| `tests/test_voice_adapter.py` | 18 smoke/unit tests (all pass) |
| `README.md` | Added *Per-agent voices for OpenClaw (pilot)* section |
| `CHANGELOG.md` | Added unreleased entry |

---

## Run the demo

```bash
cd /path/to/VoiceDNA
PYTHONPATH=. VOICEDNA_OPENCLAW_PRESETS=1 python examples/openclaw_voicedemo.py
```

Output WAVs are written to `examples/openclaw/output/`:
- `namshub_neutral.wav`
- `david_friendly.wav`
- `voss_flair.wav`

> Note: `PYTHONPATH=.` is required until the package is installed in the active environment
> (`pip install -e .` in a venv, or `pip install voicedna`).

---

## Run the tests

```bash
cd /path/to/VoiceDNA
pytest tests/test_voice_adapter.py -q
# OR: python -m pytest tests/test_voice_adapter.py -q
```

All 18 tests should pass in ~3 s.

---

## Opt-in configuration

The adapter does **not** change any existing CLI or SDK behaviour.

| Mechanism | Effect |
|-----------|--------|
| `VOICEDNA_OPENCLAW_PRESETS=1` | Signals opt-in mode (checked by demo script; no-op in library) |
| `VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:id":"preset"}'` | Auto-populates `AGENT_PRESETS` via `load_presets_from_env()` |
| Direct `VoiceAdapter(agent_presets={...})` | Fully explicit, no env needed |

---

## Assumptions

1. **TTS backend**: Uses `_SimpleLocalTTS` (espeak-ng if available, otherwise a synthetic WAV tone).
   This keeps the demo cloud-free and dependency-minimal. Replace with `PersonaPlexTTS` or `PiperTTS`
   for production quality by overriding `adapter._tts`.

2. **VoiceDNA objects**: Built synthetically from preset params via `VoiceDNA.create_new()`.
   No `.voicedna.enc` file is required for this pilot.

3. **VoiceDNAProcessor.synthesize_and_process**: Falls back to `processor.process(raw_audio, dna, params)`
   if `synthesize_and_process` is unavailable (older API compat guard).

4. **Preset names**: `neutral`, `friendly`, `flair` match the design doc verbatim.

5. **No new packaging deps**: The adapter imports only from `voicedna.*` and stdlib.

---

## Known limitations / future work

- Production audio quality depends on the TTS backend configured (`_tts` attribute).
- No persistent preset store; mappings are in-memory or from env JSON.
- `VOICEDNA_OPENCLAW_PRESETS=1` is a signal convention only; full OpenClaw plugin wiring
  would use the hook pattern in `examples/openclaw/voicedna_tts_hook.py`.
