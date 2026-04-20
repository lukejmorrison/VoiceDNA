# VoiceDNA → OpenClaw final integration checklist

Status: research complete; VoiceDNA source tree is present locally at `/home/namshub/dev/VoiceDNA`.

## What to use for the repo source
- Local tree exists: `/home/namshub/dev/VoiceDNA`
- If you need a clean checkout instead:
  ```bash
  git clone https://github.com/lukejmorrison/VoiceDNA.git /home/namshub/dev/VoiceDNA
  ```
- If you only need the published package in a fresh env instead of a checkout:
  ```bash
  python -m pip install voicedna==3.1.1
  ```

## Current compatibility verdict
- The per-agent voice pilot is already implemented in VoiceDNA (`voicedna/openclaw_adapter.py`, `examples/openclaw_voicedemo.py`, `tests/test_voice_adapter.py`, `tests/test_openclaw_live_voice.py`).
- The integration is additive and opt-in via `VOICEDNA_OPENCLAW_PRESETS=1`.
- The shipped preset set is only `neutral`, `friendly`, and `flair`.
- VoiceDNA is MIT licensed; no bundled third-party preset asset was identified that blocks the pilot.

## Implementer checklist

1. **Confirm local repo state**
   ```bash
   cd /home/namshub/dev/VoiceDNA
   git status --short --branch
   git branch --show-current
   ```

2. **Install VoiceDNA in editable mode if needed**
   ```bash
   cd /home/namshub/dev/VoiceDNA
   python -m pip install -e ".[dev]"
   ```

3. **Verify the adapter contract**
   - File: `voicedna/openclaw_adapter.py`
   - Expected API:
     - `VoiceAdapter.select_preset(agent_id, agent_name=None)`
     - `VoiceAdapter.synthesize(text, preset, output_path=None)`
   - Resolution order: `agent_id` → `agent_name` → default preset.

4. **Keep the routing opt-in**
   - Env gate:
     ```bash
     export VOICEDNA_OPENCLAW_PRESETS=1
     export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
     ```

5. **Wire OpenClaw only at the TTS boundary**
   - Recommended runtime seam: `tools/voicedna_tts_hook.py:render_agent_voice(...)` in OpenClaw.
   - Keep fallback behavior unchanged when the hook is disabled or returns `None`.

6. **Use the built-in demo for smoke validation**
   - File: `examples/openclaw_voicedemo.py`
   - Expected outputs:
     - `examples/openclaw/output/namshub_neutral.wav`
     - `examples/openclaw/output/david_friendly.wav`
     - `examples/openclaw/output/voss_flair.wav`

7. **Run the tests**
   ```bash
   cd /home/namshub/dev/VoiceDNA
   python -m pytest tests/test_voice_adapter.py -q
   python -m pytest tests/test_openclaw_live_voice.py -q
   python -m pytest -q
   ```

8. **Validate generated WAVs**
   ```bash
   file /home/namshub/dev/VoiceDNA/examples/openclaw/output/*.wav
   python - <<'PY'
   from pathlib import Path
   import wave
   root = Path('/home/namshub/dev/VoiceDNA/examples/openclaw/output')
   for p in sorted(root.glob('*.wav')):
       with wave.open(str(p), 'rb') as w:
           print(p.name, w.getnchannels(), w.getframerate(), w.getsampwidth(), w.getnframes())
           assert w.getnchannels() == 1
           assert w.getframerate() == 22050
           assert w.getsampwidth() == 2
   PY
   ```

9. **Document rollout / rollback**
   - Rollout: set the env vars and keep the OpenClaw hook in the TTS boundary.
   - Rollback: unset `VOICEDNA_OPENCLAW_PRESETS` and `VOICEDNA_OPENCLAW_PRESETS_MAP`, then remove the hook call.

## Deliverable files in `VoiceDNA/research/`
- `final_integration_checklist.md` — this file
- `ci_and_push_notes.md` — push/PR guidance and PAT decision
- `demo_commands.sh` — exact smoke/demo commands
- `voice_license_report.md` — license / preset compatibility notes

## Handoff target for implementation
- Suggested branch: `feature/voicedna-openclaw-per-agent-voices`
- Keep the feature additive; do not change default VoiceDNA behavior.
- Touch only the narrowest live audio call site in OpenClaw.
