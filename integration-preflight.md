# VoiceDNA → OpenClaw Per-Agent Voice Preflight

## Goal
Wire VoiceDNA v3.1.1 into OpenClaw’s per-agent voice path without changing default TTS behavior.

## Verified local artifacts
- `voicedna/openclaw_adapter.py`
- `voicedna/openclaw_live_voice.py`
- `examples/openclaw_voicedemo.py`
- `tests/test_voice_adapter.py`
- `tests/test_openclaw_live_voice.py`
- Demo WAVs already present and valid:
  - `examples/openclaw/output/namshub_neutral.wav`
  - `examples/openclaw/output/david_friendly.wav`
  - `examples/openclaw/output/voss_flair.wav`

## Required env vars
```bash
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

## Integration checklist
1. **Confirm repo state**
   ```bash
   cd /home/namshub/dev/VoiceDNA
   git status --short --branch
   git branch --show-current
   ```

2. **Keep the feature opt-in**
   - Only route through `voicedna.openclaw_live_voice.render_agent_voice(...)` when `VOICEDNA_OPENCLAW_PRESETS=1` is set.
   - Preserve OpenClaw’s existing TTS path when the flag is absent.

3. **Use the fallback chain**
   - exact `agent_id`
   - `agent_name` alias
   - default preset (`neutral`)

4. **Run the demo**
   ```bash
   cd /home/namshub/dev/VoiceDNA
   VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
   ```

5. **Run tests**
   ```bash
   cd /home/namshub/dev/VoiceDNA
   python -m pytest tests/test_voice_adapter.py -q
   python -m pytest tests/test_openclaw_live_voice.py -q
   ```

6. **Validate the WAVs**
   ```bash
   file /home/namshub/dev/VoiceDNA/examples/openclaw/output/*.wav
   python - <<'PY'
   from pathlib import Path
   import wave
   root = Path('/home/namshub/dev/VoiceDNA/examples/openclaw/output')
   for p in sorted(root.glob('*.wav')):
       with wave.open(str(p), 'rb') as w:
           print(p.name, w.getnchannels(), w.getframerate(), w.getsampwidth(), w.getnframes())
   PY
   ```

7. **Wire into OpenClaw**
   - Import the bridge only at the TTS post-processing boundary.
   - Do not change default semantics or require cloud APIs.
   - Keep the three pilot presets only: `neutral`, `friendly`, `flair`.

## Build / test commands
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -q
python -m pytest tests/test_openclaw_live_voice.py -q
python examples/openclaw_voicedemo.py
```

## Runbook snippet
```bash
cd /home/namshub/dev/VoiceDNA
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
PYTHONPATH=. python examples/openclaw_voicedemo.py
python -m pytest tests/test_voice_adapter.py -q
python -m pytest tests/test_openclaw_live_voice.py -q
file examples/openclaw/output/*.wav
```

## GitHub / permission notes
- **No PAT is required** for this pilot as long as you do **not** touch `.github/workflows/*` or other workflow files.
- If a later change must modify GitHub Actions/workflow files, use a short-lived PAT with `workflow` scope before pushing.

## Blockers / next steps for Dr Voss
- No blocking repo issue found in the current pilot tree.
- Implement the OpenClaw hook at the TTS boundary only.
- Keep the env-guarded path additive and reversible.
- If workflow files are introduced later, stop and request a `workflow`-scoped PAT before pushing.
