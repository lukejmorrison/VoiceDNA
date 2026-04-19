# PR Draft — VoiceDNA OpenClaw Per-Agent Voices

**Branch:** `feature/voicedna-openclaw-per-agent-voices`  
**Target:** `main`  
**Status:** Ready for review — READY_TO_PUSH  
**Date:** 2026-04-18

---

## Title

`feat: wire VoiceDNA VoiceAdapter into OpenClaw agent voice pipeline`

---

## Summary

Adds per-agent voice preset support to OpenClaw via a new `VoiceAdapter` class in the VoiceDNA SDK. Agents are mapped to voice presets (`neutral`, `friendly`, `flair`) by agent ID, with environment-driven or programmatic configuration. Feature is fully opt-in and additive — no breaking changes.

---

## Changes

| File | Purpose |
|------|---------|
| `voicedna/openclaw_adapter.py` | VoiceAdapter class (preset registry, agent mapping, synthesis) |
| `examples/openclaw_voicedemo.py` | Demo script producing 3 WAV files |
| `examples/openclaw/output/*.wav` | Demo artifacts (164–211 KB each, PCM 16-bit 22050 Hz) |
| `tests/test_voice_adapter.py` | 18 unit tests |
| `tests/test_openclaw_live_voice.py` | 13 integration tests |
| `INTEGRATION_NOTE.md` | Wiring documentation |
| `DESIGN_DOC.md` | Architecture reference |
| `VERIFICATION_REPORT.md` | Full test + artifact verification |
| `PR_OPENCLAW_VOICES.md` | PR description (detailed) |

---

## Test Results

```
31 passed in 2.09s
```

- `tests/test_voice_adapter.py` — 18 unit tests: all pass
- `tests/test_openclaw_live_voice.py` — 13 integration tests: all pass
- Linting: `ruff check .` — All checks passed

---

## Demo Verification

```
examples/openclaw/output/namshub_neutral.wav   — 164,696 B  ✅
examples/openclaw/output/david_friendly.wav    — 211,876 B  ✅
examples/openclaw/output/voss_flair.wav        — 209,542 B  ✅
```

All files validated: RIFF/WAVE, PCM 16-bit, mono, 22050 Hz.

---

## How to Verify Locally

```bash
cd /home/namshub/dev/VoiceDNA

# Run all tests
python -m pytest tests/test_voice_adapter.py tests/test_openclaw_live_voice.py -v

# Re-run demo
python examples/openclaw_voicedemo.py

# Inspect a WAV
python -c "import wave; w=wave.open('examples/openclaw/output/voss_flair.wav'); print(w.getparams())"
```

---

## Checklist

- [x] Core implementation: `voicedna/openclaw_adapter.py`
- [x] Demo script runs end-to-end
- [x] Demo WAVs generated and validated
- [x] 31 tests pass (unit + integration)
- [x] Linting passes (ruff)
- [x] No breaking changes to existing VoiceDNA API
- [x] No secrets committed
- [x] No GitHub Actions workflow changes
- [x] Documentation complete (INTEGRATION_NOTE, DESIGN_DOC, VERIFICATION_REPORT)
- [ ] Push to remote (normal repo auth only; workflow-scope PAT not needed unless `.github/workflows/*` changes are added later)
- [ ] Open GitHub PR

---

## Push Instructions

```bash
# Direct push (requires GitHub PAT or existing auth)
cd /home/namshub/dev/VoiceDNA
git push origin feature/voicedna-openclaw-per-agent-voices

# Offline bundle (if no direct push available)
git bundle create /tmp/feat-voicedna-openclaw.bundle \
  feature/voicedna-openclaw-per-agent-voices ^main
```

---

## Blockers

- **Push requires GitHub PAT** — no remote push has been performed per constraints.
- No other blockers.
