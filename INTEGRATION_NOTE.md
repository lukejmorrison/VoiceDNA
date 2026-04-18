# INTEGRATION_NOTE.md — VoiceDNA OpenClaw Adapter Wiring

**Branch:** `feature/voicedna-openclaw-per-agent-voices`  
**Date:** 2026-04-18  
**Author:** Dr Voss Thorne

---

## What Changed

| File | Description |
|------|-------------|
| `voicedna/openclaw_adapter.py` | New `VoiceAdapter` class — per-agent preset selection, synthesis, env-driven opt-in via `VOICEDNA_OPENCLAW_PRESETS_MAP` |
| `examples/openclaw_voicedemo.py` | Runnable demo: 3 agents × 3 presets → WAV output in `examples/openclaw/output/` |
| `tests/test_voice_adapter.py` | 18 unit/smoke tests covering preset registry, selection, env loading, synthesis paths |
| `README.md` | Per-agent voices section added |
| `CHANGELOG.md` | Unreleased entry added for pilot |
| `DESIGN_DOC.md` | 1-page design description of the wiring approach |

Demo WAVs committed at:
- `examples/openclaw/output/namshub_neutral.wav` (77 KB)
- `examples/openclaw/output/david_friendly.wav` (104 KB)
- `examples/openclaw/output/voss_flair.wav` (109 KB)

---

## How to Validate Locally

```bash
cd /path/to/VoiceDNA
git checkout feature/voicedna-openclaw-per-agent-voices

# 1. Run adapter tests (no synthesis backend required)
pytest tests/test_voice_adapter.py -v
# Expected: 18 passed

# 2. Run linter
ruff check voicedna/openclaw_adapter.py tests/test_voice_adapter.py examples/openclaw_voicedemo.py
# Expected: All checks passed!

# 3. Run the demo (synthesis backend must be installed)
VOICEDNA_OPENCLAW_PRESETS=1 python examples/openclaw_voicedemo.py
# Expected: 3 WAV files written to examples/openclaw/output/

# 4. Verify WAVs
file examples/openclaw/output/*.wav
# Expected: each is RIFF (little-endian) data, WAVE audio
```

---

## Opt-in Activation

The adapter is **disabled by default**. To enable per-agent preset routing:

```bash
# Option A: env var for preset map (JSON)
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:dr-voss-thorne":"flair","agent:david-hardman":"friendly"}'

# Option B: direct construction in code
from voicedna.openclaw_adapter import VoiceAdapter
adapter = VoiceAdapter(agent_presets={"agent:namshub": "neutral"})
preset = adapter.select_preset("agent:namshub")
```

---

## Push / PR Instructions

The branch is already on `origin/feature/voicedna-openclaw-per-agent-voices`.  
To push this local state:

```bash
cd /home/namshub/dev/VoiceDNA
git push origin feature/voicedna-openclaw-per-agent-voices
```

If push is blocked, use the bundle at `/tmp/voiceDNA_voicedna_bundle.bundle`:

```bash
# On recipient machine:
git clone /tmp/voiceDNA_voicedna_bundle.bundle voicedna-bundle
cd voicedna-bundle
git checkout feature/voicedna-openclaw-per-agent-voices
```
