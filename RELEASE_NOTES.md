# VoiceDNA Release Notes

## v3.1.1 — 2026-04-18

**Post-merge polish for the per-agent voice pilot.**

### Changes since v3.1.0
- Refreshed demo WAVs and test-output snapshot committed to main.
- RELEASE_CHECKLIST and local test report added.
- Stale duplicate PR #6 closed; feature canonical entry point is PR #5 (merged 2026-04-14).

### Merge commit
e605826

---

## v3.1.0 — 2026-04-18

**Per-agent voice pilot: VoiceAdapter + OpenClaw demo (3 presets).**

Introduces `voicedna/openclaw_adapter.py` — a lightweight, opt-in adapter that maps OpenClaw agent identities to distinct VoiceDNA voice presets.

### What's new
- **`VoiceAdapter` class** (`voicedna/openclaw_adapter.py`): `select_preset(agent_id, agent_name)` → deterministic routing; `synthesize(text, preset, output_path)` → WAV generation; `load_presets_from_env()` for runtime overrides.
- **3 pilot presets**: `neutral` (Namshub), `friendly` (David Hardman), `flair` (Dr Voss Thorne).
- **Demo script** (`examples/openclaw_voicedemo.py`): generates 3 agent × preset WAV files under `examples/openclaw/output/`.
- **Verified demo WAVs**: `namshub_neutral.wav`, `david_friendly.wav`, `voss_flair.wav` — all valid RIFF/PCM 16-bit mono 22050 Hz.
- **18 unit tests** in `tests/test_voice_adapter.py`; 23 tests pass end-to-end (0 failed).

### Opt-in behavior
Feature is inactive unless `VOICEDNA_OPENCLAW_PRESETS=1` is set or `VoiceAdapter` is imported directly. No breaking changes to existing CLI, SDK API, or packaged presets.

### PR
[#5 — feat: per-agent voice pilot](https://github.com/lukejmorrison/VoiceDNA/pull/5) — merged 2026-04-14.
Merge commit: `59ad26b`
