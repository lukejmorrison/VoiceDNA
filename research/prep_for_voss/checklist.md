# Prep for Dr Voss — VoiceDNA → OpenClaw

## Top 5 prioritized tasks

### 1) Confirm the exact OpenClaw TTS seam
Find the narrowest call site that already knows `agent_id` and, if available, `agent_name`.

Why first:
- the bridge should only live at the TTS boundary
- no broader refactor is needed
- rollback stays trivial

### 2) Wire VoiceDNA only behind the env gate
Call `render_agent_voice(...)` only when `VOICEDNA_OPENCLAW_PRESETS=1` is set.

Keep behavior:
- env off → return `None` and preserve existing OpenClaw TTS
- env on → route through `VoiceAdapter`

### 3) Validate the VoiceDNA contract locally
Run the adapter and live-bridge tests before touching the live OpenClaw path.

### 4) Generate and verify demo WAVs
Produce the three preset WAVs locally and check they are valid RIFF/WAVE files.

### 5) Prepare the handoff / push path
If a push is needed, choose the safest route first:
- bundle handoff
- user-side push
- PAT only if Luke explicitly approves it

---

## Exact files to use
### VoiceDNA repo
- `voicedna/openclaw_adapter.py`
- `voicedna/openclaw_live_voice.py`
- `examples/openclaw_voicedemo.py`
- `tests/test_voice_adapter.py`
- `tests/test_openclaw_live_voice.py`

### Reference hook examples
- `examples/openclaw/voicedna_tts_hook.py`
- `examples/openclaw_hook.py`
- `examples/openclaw_skill.py`

### Research docs
- `research/voicedna_integration_summary.md`
- `research/implementation_checklist.md`
- `research/openclaw_integration_prep.md`
- `research/voicedna_openclaw_integration_checklist.md`
- `research/DESIGN_DOC.md`

---

## Reproducible local commands

### 1) Run the unit tests
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -q
python -m pytest tests/test_openclaw_live_voice.py -q
```

### 2) Run the smoke test / demo
```bash
cd /home/namshub/dev/VoiceDNA
bash research/smoke_test_tts.sh
```

### 3) Run the demo and generate WAVs directly
```bash
cd /home/namshub/dev/VoiceDNA
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
PYTHONPATH=. python examples/openclaw_voicedemo.py
```

Expected outputs:
- `examples/openclaw/output/namshub_neutral.wav`
- `examples/openclaw/output/david_friendly.wav`
- `examples/openclaw/output/voss_flair.wav`
- `research/demo_output/demo.wav`

### 4) Verify the files
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

### 5) Optional editable install for cleaner imports
```bash
cd /home/namshub/dev/VoiceDNA
pip install -e .
```

---

## Blockers and exact remediation

### Blocker A — GitHub push / PR may require a PAT
If Dr Voss needs to push this branch from the host, GitHub may reject it without a valid token.

Minimal remediation options:
1. preferred: create a git bundle and hand it off
2. preferred: push from Luke’s trusted machine
3. only if explicitly approved: use a short-lived PAT

If Luke approves a PAT, use the smallest possible scope and keep it short-lived.

### Blocker B — external TTS backends may require API keys or model files
This only matters if the implementation chooses a non-local backend path.

Minimal remediation:
- keep the pilot local-first
- do not enable cloud backends unless the relevant key is already configured
- if a backend is selected, set the backend-specific key or model path before running the demo

### Blocker C — VoiceDNA runtime packages may be missing
If synthesis raises a “not installed” runtime error:

Minimal remediation:
```bash
cd /home/namshub/dev/VoiceDNA
pip install -e .
```

If the feature needs optional extras, install the specific extra instead:
- `pip install "voicedna[consistency]"`
- `pip install "voicedna[rvc]"`
- `pip install "voicedna[personaplex]"`
- `pip install "voicedna[personaplex-lowvram]"`

---

## Implementation checklist for Dr Voss
- [ ] Confirm the live TTS call site and agent identity source
- [ ] Import `render_agent_voice(...)` only at that boundary
- [ ] Keep `VOICEDNA_OPENCLAW_PRESETS` as the only enable switch
- [ ] Preserve pass-through behavior when the flag is off
- [ ] Run the VoiceDNA tests and demo locally
- [ ] Validate generated WAV headers and sizes
- [ ] Decide bundle vs push vs PAT before any publish step

---

## One-line handoff summary
Wire VoiceDNA at the narrow OpenClaw TTS boundary, keep it opt-in via `VOICEDNA_OPENCLAW_PRESETS`, validate locally with the two pytest files plus the demo, then choose the safest push path only after the WAVs are confirmed.