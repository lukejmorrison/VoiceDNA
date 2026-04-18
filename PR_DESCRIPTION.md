# feat: per-agent voice pilot — VoiceAdapter + OpenClaw demo (3 presets)

**PR:** https://github.com/lukejmorrison/VoiceDNA/pull/5  
**Branch:** `feature/voicedna-openclaw-per-agent-voices` → `main`  
**Status:** OPEN (draft)

---

## Summary

Introduces `voicedna/openclaw_adapter.py` — a lightweight, opt-in adapter that maps OpenClaw agent identities to VoiceDNA voice presets, enabling distinct per-agent TTS voices across the Namshub / Dr Voss Thorne / David Hardman personas without changing default VoiceDNA behavior.

---

## Changelog

### Added
- `voicedna/openclaw_adapter.py` — `VoiceAdapter` class with:
  - `select_preset(agent_id, agent_name, default)` — deterministic preset lookup
  - `synthesize(text, preset, out_path)` — audio synthesis to WAV
  - `load_presets_from_env(env_map)` — opt-in env-driven agent→preset mapping
  - `register_agent(agent_id, preset)` — runtime registration
  - 3 pilot presets: `neutral`, `friendly`, `flair`
- `examples/openclaw_voicedemo.py` — demo generating 3 agents × 3 presets → WAV output
- `tests/test_voice_adapter.py` — 18 unit tests covering all adapter paths

### Updated
- `README.md` — per-agent voice section
- `CHANGELOG.md` — v2.1.0 entry
- `IMPLEMENTATION_NOTE.md` — integration notes

---

## Test Evidence

**Run date:** 2026-04-17  
**Python:** 3.14.4  
**pytest:** 9.0.3

```
34 passed in 1.66s
0 failed, 0 errors
```

Full test log: `test-output.txt`

Test files executed:
- `tests/test_audio_roundtrip.py` — 1 passed
- `tests/test_child_inheritance.py` — 3 passed
- `tests/test_consistency_engine.py` — 2 passed
- `tests/test_natural_backend_lowvram.py` — 3 passed
- `tests/test_natural_doctor.py` — 2 passed
- `tests/test_piper_quality.py` — 3 passed
- `tests/test_processor_report.py` — 2 passed
- `tests/test_voice_adapter.py` — 18 passed

---

## Demo WAV Validation

All 3 demo WAVs generated and validated as playable:

| File | Duration | Rate | Channels |
|------|----------|------|----------|
| `namshub_neutral.wav` | 3.73s | 22050 Hz | 1 (mono) |
| `david_friendly.wav` | 4.80s | 22050 Hz | 1 (mono) |
| `voss_flair.wav` | 4.75s | 22050 Hz | 1 (mono) |

Location: `examples/openclaw/output/`

---

## Usage Notes

### Minimal usage
```python
from voicedna.openclaw_adapter import VoiceAdapter

adapter = VoiceAdapter()
preset = adapter.select_preset(agent_id="dr-voss-thorne")
audio = adapter.synthesize("Hello from Dr Voss Thorne.", preset=preset)
```

### Per-agent mapping via env
```bash
export VOICEDNA_AGENT_PRESETS='{"dr-voss-thorne": "flair", "namshub": "neutral"}'
```

### Run demo
```bash
python examples/openclaw_voicedemo.py
# Output: examples/openclaw/output/{namshub_neutral,david_friendly,voss_flair}.wav
```

### Run tests
```bash
python -m pytest tests/ -v
```

---

## Rollout / Rollback

**Rollout:** Merge behind opt-in config. No changes to existing VoiceDNA defaults.  
**Rollback:** Disable `VOICEDNA_AGENT_PRESETS` env var or revert this PR.

---

## Dependency Note

`cryptography` package required (in `requirements.txt`). Install via:
```bash
sudo pacman -S python-cryptography  # Arch Linux
# or: pip install cryptography
```
