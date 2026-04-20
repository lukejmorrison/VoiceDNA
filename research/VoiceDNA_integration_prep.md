# VoiceDNA ↔ OpenClaw integration prep

**Goal:** wire VoiceDNA’s per-agent voice routing into OpenClaw as an opt-in, additive TTS layer.

## 1) What `VoiceAdapter` exposes

**Backing file:** `voicedna/openclaw_adapter.py`

### Public surface
- `VoiceAdapter(agent_presets: dict[str, str] | None = None, default_preset: str = "neutral")`
- `select_preset(agent_id: str, agent_name: str | None = None) -> str`
  - resolution order: `agent_id` → `agent_name` → `default_preset`
- `synthesize(text: str, preset: str, output_path: str | None = None) -> bytes`
  - returns WAV bytes
  - optionally writes the WAV to disk
- preset registry is built in:
  - `neutral`
  - `friendly`
  - `flair`

### How TTS is produced
- Adapter builds a VoiceDNA profile for the chosen preset, then calls local synthesis.
- Runtime backend path uses:
  - `voice_dna.VoiceDNA`
  - `voicedna.framework.VoiceDNAProcessor`
  - `voicedna.synthesis._SimpleLocalTTS`
- Output format validated in tests/demo: **RIFF PCM, 16-bit, mono, 22050 Hz**.

### How VoiceDNA is exposed
- **Python API:** `from voicedna.openclaw_adapter import VoiceAdapter`
- **Env-configured preset map:** `VOICEDNA_OPENCLAW_PRESETS_MAP`
- **Opt-in gate:** `VOICEDNA_OPENCLAW_PRESETS=1`
- **Demo hook:** `examples/openclaw_voicedemo.py`

---

## 2) Exact OpenClaw file-level wiring needed

### Canonical integration point
- `tools/voicedna_tts_hook.py`
  - function: `render_agent_voice(text, agent_id, agent_name=None, output_path=None) -> bytes | None`
  - this is the recommended OpenClaw TTS post-processor entrypoint
  - returns `None` when disabled, so existing TTS can fall back unchanged

### Shim / gate
- `tools/voicedna_adapter.py`
  - function: `get_voice_adapter() -> VoiceAdapter | None`
  - function: `reset_adapter() -> None`
  - config keys:
    - `VOICEDNA_OPENCLAW_PRESETS`
    - `VOICEDNA_OPENCLAW_PRESETS_MAP`

### Registry config
- `skills/voice-dna-registry/registry.json`
  - `hook.enabled: true`
  - `hook.source: /home/namshub/.openclaw/workspaces/namshub/main/VoiceDNA/examples/openclaw/voicedna_tts_hook.py`
  - `passwordEnv: VOICEDNA_PASSWORD_NAMSHUB` for encrypted voice material

### Call-site change required in OpenClaw
Wherever OpenClaw currently converts text → TTS audio, call:

```python
from tools.voicedna_tts_hook import render_agent_voice

wav_bytes = render_agent_voice(
    text=tts_text,
    agent_id=agent.id,
    agent_name=getattr(agent, "name", None),
    output_path=maybe_output_path,
)
if wav_bytes is None:
    # existing TTS/provider path
    ...
else:
    # deliver wav_bytes
    ...
```

**Practical target files in the OpenClaw tree:**
- `tools/voicedna_tts_hook.py` for the hook API
- `tools/voicedna_adapter.py` for opt-in singleton/config
- the existing TTS call site that emits agent audio (the hook is designed to be dropped in there)
- `skills/audio-responder-tts/audio_tts_reply.sh` only if you want the manual reply script to use the same hook

### Docs/tests to keep aligned
- `tests/test_voicedna_adapter.py`
- `tests/test_voicedna_tts_hook.py`
- `tests/test_voicedna_e2e.py`
- `README.md` / `docs/VOICE_DNA_HANDOFF.md` / `docs/voicedna-integration.md` if user-facing docs are updated

---

## 3) Runtime dependencies, env vars, packaging notes

### Required runtime deps
VoiceDNA repo must be importable locally and have the synthesis stack available:
- `voice_dna`
- `voicedna`
- `numpy`
- `pydub`
- `sounddevice`
- `cryptography`
- any backend deps needed by the chosen local TTS path

### OpenClaw-side env vars
- `VOICEDNA_OPENCLAW_PRESETS=1` — master opt-in; unset means no behavior change
- `VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'`
- if encrypted registry voices are used:
  - `VOICEDNA_PASSWORD_NAMSHUB` (or the password env name stored in the registry for the agent)

### Packaging notes
- Keep the VoiceDNA import path local; the shim path-injects `/home/namshub/dev/VoiceDNA`.
- Do not require cloud credentials for the pilot demo.
- Avoid adding secrets to git-tracked files; passwords stay in environment only.

---

## 4) Smoke-test plan

### Produce demo WAVs
```bash
cd /home/namshub/dev/VoiceDNA
python examples/openclaw_voicedemo.py
```

Expected output files:
- `examples/openclaw/output/namshub_neutral.wav`
- `examples/openclaw/output/david_friendly.wav`
- `examples/openclaw/output/voss_flair.wav`

### Verify sample rate / format
```bash
python - <<'PY'
from pathlib import Path
import wave
root = Path('/home/namshub/dev/VoiceDNA/examples/openclaw/output')
for p in sorted(root.glob('*.wav')):
    with wave.open(str(p), 'rb') as w:
        print(p.name, 'channels=', w.getnchannels(), 'rate=', w.getframerate(), 'width=', w.getsampwidth(), 'frames=', w.getnframes())
        assert w.getnchannels() == 1
        assert w.getframerate() == 22050
        assert w.getsampwidth() == 2
PY
```

Optional quick header check:
```bash
file /home/namshub/dev/VoiceDNA/examples/openclaw/output/*.wav
```

### Relevant tests
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -q
python -m pytest tests/test_openclaw_live_voice.py -q
python -m pytest -q
```

---

## 5) PR checklist

- [ ] Confirm the hook is still opt-in and default OpenClaw TTS behavior is unchanged
- [ ] Confirm `render_agent_voice()` is invoked only at the TTS output boundary
- [ ] Confirm fallback to the existing TTS provider when the hook returns `None`
- [ ] Confirm the preset map covers `agent:namshub`, `agent:david-hardman`, `agent:dr-voss-thorne`
- [ ] Confirm demo WAVs are generated locally and match 22050 Hz / mono / 16-bit
- [ ] Confirm unit tests + integration tests pass
- [ ] Confirm no secret values are committed
- [ ] Confirm docs mention `VOICEDNA_OPENCLAW_PRESETS` and `VOICEDNA_OPENCLAW_PRESETS_MAP`

---

## 6) Blocking decisions / missing credentials

1. **Decision needed:** which OpenClaw call site becomes the canonical TTS hook boundary. Recommendation: use `tools/voicedna_tts_hook.render_agent_voice()` as the single integration point.
2. **Credential needed only if using encrypted registry voices:** the per-agent password env var value, e.g. `VOICEDNA_PASSWORD_NAMSHUB`.
3. **Dependency requirement:** VoiceDNA must be present locally at the expected repo path and the local synthesis backend must be importable.

**Bottom line:** no cloud/API credential is required for the demo path; the only real blocker is deciding the exact TTS call site and providing any encrypted-voice password(s) if the registry-backed flow is enabled.
