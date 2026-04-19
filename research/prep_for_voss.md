# VoiceDNA → OpenClaw per-agent voice prep for Dr Voss

Scope: research-only handoff for wiring `VoiceDNA v3.1.1` `VoiceAdapter` into the OpenClaw per-agent voice path.

## 1) What to touch in OpenClaw

The OpenClaw repo already exposes the seam; the minimal consumer-side hooks are:

### Core wiring
- `/home/luke/dev/openclaw/tools/voicedna_adapter.py`
  - `is_voicedna_enabled()` — opt-in gate (`VOICEDNA_OPENCLAW_PRESETS`)
  - `_build_preset_map()` — env/default preset map resolution
  - `get_voice_adapter()` — singleton adapter construction
  - `reset_adapter()` — test/runtime reset hook
- `/home/luke/dev/openclaw/tools/voicedna_tts_hook.py`
  - `render_agent_voice(text, agent_id, agent_name=None, output_path=None)` — canonical TTS seam
  - `is_voicedna_enabled()` — re-exported gate
- `/home/luke/dev/openclaw/demo/voicedna_demo.py`
  - `validate_wav()` — confirms RIFF / PCM16 / mono / 22050 Hz
  - `main()` — demo output generation

### Tests already present on the OpenClaw side
- `/home/luke/dev/openclaw/tests/test_voicedna_adapter.py`
- `/home/luke/dev/openclaw/tests/test_voicedna_e2e.py`

### Minimal patch/hook if a live caller still needs wiring
If the actual TTS producer still bypasses `tools/voicedna_tts_hook.py`, patch the caller that emits audio bytes so it does this first:

```python
from tools.voicedna_tts_hook import render_agent_voice

wav_bytes = render_agent_voice(text, agent_id=agent.id, agent_name=agent.name, output_path=maybe_path)
if wav_bytes is not None:
    return wav_bytes
# else fall back to existing TTS path
```

That keeps OpenClaw behavior unchanged unless `VOICEDNA_OPENCLAW_PRESETS=1` is set.

## 2) VoiceDNA v3.1.1: release / API surface check

### Confirmed locally
- Git tag exists: `v3.1.1`
- The pilot docs in this repo explicitly reference `VoiceDNA v3.1.1`
- Release artifact bundle present: `release/voicedna_openclaw_per_agent_voices.bundle`

### API surface to rely on
`voicedna.openclaw_adapter.VoiceAdapter`

Methods / members:
- `select_preset(agent_id, agent_name=None) -> str`
- `synthesize(text, preset, output_path=None) -> bytes`
- `register_agent(agent_id, preset) -> None`
- `presets` property

Module helpers / data:
- `PRESET_REGISTRY`
- `DEFAULT_PRESET`
- `AGENT_PRESETS`
- `load_presets_from_env()`

### Usage snippet
```python
from voicedna.openclaw_adapter import VoiceAdapter

adapter = VoiceAdapter(agent_presets={
    "agent:namshub": "neutral",
    "agent:david-hardman": "friendly",
    "agent:dr-voss-thorne": "flair",
})

preset = adapter.select_preset("agent:dr-voss-thorne", agent_name="Dr Voss Thorne")
wav_bytes = adapter.synthesize("Precision is the only acceptable standard.", preset)
```

## 3) Audio format: confirmed

Confirmed by the demo + tests:
- Container: `RIFF/WAVE`
- Encoding: PCM (`audio_format == 1`)
- Channels: mono (`1`)
- Sample rate: `22050 Hz`
- Bit depth: `16-bit`

So the PROJECTS.md note is correct for this pilot: **RIFF PCM 16-bit mono 22050 Hz**.

### Conversion guidance
No conversion is needed for the current OpenClaw demo path because `VoiceAdapter.synthesize()` already returns WAV bytes in the expected format.

Only convert if a downstream consumer demands a different transport format. In that case use `ffmpeg` or the consumer’s native resampler after synthesis.

## 4) Exact test / validation commands

### VoiceDNA repo
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -v
python -m pytest tests/test_openclaw_live_voice.py -v
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
```

### OpenClaw repo
```bash
cd /home/luke/dev/openclaw
python -m pytest tests/test_voicedna_adapter.py tests/test_voicedna_e2e.py -v
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=/home/namshub/dev/VoiceDNA python demo/voicedna_demo.py
```

### Quick header check for generated WAVs
```bash
python - <<'PY'
from pathlib import Path
import struct
for p in Path('/home/namshub/dev/VoiceDNA/examples/openclaw/output').glob('*.wav'):
    data = p.read_bytes()
    assert data[:4] == b'RIFF' and data[8:12] == b'WAVE', p
    fmt, ch, rate, _, _, bits = struct.unpack_from('<HHIIHH', data, 20)
    assert (fmt, ch, rate, bits) == (1, 1, 22050, 16), (p, fmt, ch, rate, bits)
    print('OK', p)
PY
```

## 5) CI / automation guidance

Keep CI conservative:
1. Run the shim tests unconditionally:
   - OpenClaw: `tests/test_voicedna_adapter.py`
2. Run synthesis / e2e only when the runner can import the VoiceDNA checkout or an installed wheel.
3. Do **not** make CI depend on `VOICEDNA_OPENCLAW_PRESETS=1` for default success.
4. Treat the demo step as local/manual unless the backend is made available in CI on purpose.

Suggested CI steps if the backend is available:
```bash
python -m pytest tests/test_voicedna_adapter.py -v
python -m pytest tests/test_voicedna_e2e.py -v
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=/home/namshub/dev/VoiceDNA python demo/voicedna_demo.py
```

## 6) Env vars / secrets needed

### Required for opt-in routing
- `VOICEDNA_OPENCLAW_PRESETS=1`
- `VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'` (optional override)

### VoiceDNA / encrypted voice files
- `VOICEDNA_PASSWORD_NAMSHUB` for encrypted registry voice material, if that agent uses a `.voicedna.enc` artifact
- If a different agent is added, use the `passwordEnv` from `skills/voice-dna-registry/registry.json`

### Path / import assumptions
- VoiceDNA source checkout is expected at `/home/namshub/dev/VoiceDNA`
- OpenClaw repo path in this host is the symlinked shared clone: `/home/namshub/dev/openclaw -> /home/luke/dev/openclaw`

## 7) Top 3 integration tasks for Dr Voss

1. **Patch the live TTS seam** to call `render_agent_voice(...)` before default TTS output.
2. **Keep preset routing deterministic**: `agent_id -> agent_name -> default`, with the three pilot presets only.
3. **Validate artifacts end-to-end**: run both repos’ pytest targets and confirm the three WAVs are non-empty RIFF PCM 16-bit mono 22050 Hz.

## 8) Quick wins

- The adapter and tests already exist on both sides; likely only the live callsite needs a narrow hook.
- The expected audio format is already confirmed, so no format conversion work is needed for the pilot.
- The default path remains opt-in, so rollback is just unsetting the env vars.

## 9) Blockers needing Luke approval

- **PAT required** for any push / PR action.
- **CI permission / runtime access** if synthesis tests are to run on CI; otherwise keep them local/manual.
- **Secret access** for any encrypted voice artifacts (`VOICEDNA_PASSWORD_*`) if the pilot moves from synthetic presets to registry-backed voices.
- **Version metadata decision**: `pyproject.toml` still says `3.0.0` while the release/tag target is `v3.1.1`; align before publishing.

## 10) Recommended handoff note

Best next action for implementation: keep the change set narrow to the live TTS hook and avoid touching VoiceDNA core behavior unless the consumer callsite cannot already reach `render_agent_voice()`.
