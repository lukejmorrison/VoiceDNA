# VoiceDNA → OpenClaw integration design

## Objective
Add VoiceDNA per-agent voice routing to OpenClaw as an additive, opt-in TTS boundary layer. Default OpenClaw behavior must remain unchanged unless the feature flag is enabled.

## Architecture
```
OpenClaw agent identity
  → OpenClaw TTS hook / wrapper
  → VoiceDNA live bridge (`voicedna/openclaw_live_voice.py`)
  → VoiceAdapter (`voicedna/openclaw_adapter.py`)
  → VoiceDNA processor + synthesis backend
  → WAV bytes / optional file output
```

## Canonical VoiceDNA contracts
- `VoiceAdapter.select_preset(agent_id, agent_name=None) -> str`
- `VoiceAdapter.synthesize(text, preset, output_path=None) -> bytes`
- `render_agent_voice(text, agent_id, agent_name=None, output_path=None) -> bytes | None`
- `load_presets_from_env()` reads `VOICEDNA_OPENCLAW_PRESETS_MAP`

## Preset routing rules
Resolution order:
1. exact `agent_id`
2. exact `agent_name` alias
3. default preset (`neutral`)

Pilot presets only:
- `neutral`
- `friendly`
- `flair`

## Required env vars
### Feature gate
- `VOICEDNA_OPENCLAW_PRESETS=1`
  - Enables the OpenClaw bridge.
  - If absent or empty, the bridge must pass through and return `None`.

### Optional mapping override
- `VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'`
  - JSON mapping from agent id or alias to preset.
  - Invalid JSON should fail closed and fall back to built-in pilot defaults.

### VoiceDNA runtime inputs
- `VOICEDNA_ENC_PATH`
  - Path to the encrypted `.voicedna.enc` file.
- `VOICEDNA_PASSWORD`
  - Password for decrypting the VoiceDNA artifact.
- `VOICEDNA_FORCE_AGE`
  - Optional age override during processing.

## Required dependencies
### For local VoiceDNA demo / tests
- Python 3.10+ (local repo runtime)
- `voice_dna` / `voicedna` package installed from the VoiceDNA repo, ideally editable:
  - `pip install -e /home/namshub/dev/VoiceDNA`
- Core runtime libs already used by VoiceDNA:
  - `numpy`
  - `cryptography`
  - `pydub`
  - `sounddevice` when playback paths are used

### Optional backends
Only needed when you choose those features:
- `voicedna[consistency]` for speaker-consistency extras
- `voicedna[rvc]` for real RVC voice cloning
- `voicedna[personaplex]` or `voicedna[personaplex-lowvram]` for PersonaPlex natural voice
- cloud TTS backend API keys if the chosen backend is ElevenLabs / Cartesia / similar

## Implementation approach
### Phase 1 — keep it additive
1. Keep the feature behind `VOICEDNA_OPENCLAW_PRESETS`.
2. Load the adapter lazily so OpenClaw startup cost stays unchanged.
3. Preserve the existing OpenClaw TTS path when the flag is off.

### Phase 2 — narrow live seam wiring
1. Identify the exact OpenClaw function that already has `agent_id` and optionally `agent_name`.
2. Call `render_agent_voice(...)` at that TTS boundary.
3. If it returns bytes, use them.
4. If it returns `None`, continue with the existing TTS output path.

### Phase 3 — validate
1. Run the VoiceDNA adapter tests.
2. Run the live bridge tests.
3. Generate the three demo WAVs.
4. Verify the WAV headers and file sizes.

### Phase 4 — document rollback
1. Unset `VOICEDNA_OPENCLAW_PRESETS`.
2. Unset `VOICEDNA_OPENCLAW_PRESETS_MAP`.
3. Remove the narrow hook call if needed.

## API contract for OpenClaw
OpenClaw should pass the following to the bridge when available:
- `text` — the spoken content
- `agent_id` — canonical agent identifier
- `agent_name` — optional alias/human-readable name
- `output_path` — optional file path for WAV output

Bridge behavior:
- returns WAV bytes on success
- returns `None` when the opt-in flag is not set
- raises only on genuine configuration/runtime failures

## Verification commands
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -q
python -m pytest tests/test_openclaw_live_voice.py -q
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
file examples/openclaw/output/*.wav
python - <<'PY'
from pathlib import Path
import wave
root = Path('examples/openclaw/output')
for p in sorted(root.glob('*.wav')):
    with wave.open(str(p), 'rb') as w:
        print(p.name, w.getnchannels(), w.getframerate(), w.getsampwidth(), w.getnframes())
PY
```

## Step-by-step implementation checklist
1. Confirm the live OpenClaw TTS seam and agent identity source.
2. Import the bridge only at that seam.
3. Keep the env gate as the only enable switch.
4. Preserve fallback to the current OpenClaw TTS path.
5. Run unit tests and the demo locally.
6. Validate WAV output headers and sizes.
7. Only then prepare a push / PR / bundle handoff.

## Rollback
If anything behaves unexpectedly:
- unset `VOICEDNA_OPENCLAW_PRESETS`
- unset `VOICEDNA_OPENCLAW_PRESETS_MAP`
- remove the narrow hook import/call
- keep the rest of OpenClaw unchanged