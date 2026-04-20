# Implementation Note — VoiceDNA → OpenClaw Per-Agent Voice Integration

**Author:** Dr Voss Thorne  
**Date:** 2026-04-19  
**Branch:** `feature/voicedna-openclaw-per-agent-voices`  
**PR:** https://github.com/lukejmorrison/VoiceDNA/pull/8

---

## What Was Done

1. **VoiceAdapter** (`voicedna/openclaw_adapter.py`) — per-agent preset selection and synthesis engine with 3 pilot presets (`neutral`, `friendly`, `flair`). Fully opt-in via `VOICEDNA_OPENCLAW_PRESETS=1`.

2. **Live bridge** (`voicedna/openclaw_live_voice.py`) — `render_agent_voice()` entry point for OpenClaw TTS hooks. Lazy singleton VoiceAdapter. Env-driven agent→preset map via `VOICEDNA_OPENCLAW_PRESETS_MAP` (JSON).

3. **Tests** — 52 passing: `tests/test_voice_adapter.py` + `tests/test_openclaw_live_voice.py`.

4. **Demo WAVs** — 3 validated RIFF PCM 16-bit mono 22050 Hz files at:
   - `demo/namshub_neutral.wav`
   - `demo/david_friendly.wav`
   - `demo/voss_flair.wav`
   Also at `examples/openclaw/output/`.

5. **Design doc** — `DESIGN_DOC.md` (root) and `research/DESIGN_DOC_voice_integration.md`.

---

## Default Agent Mapping

| Agent ID | Preset |
|----------|--------|
| `agent:namshub` | `neutral` |
| `agent:david-hardman` | `friendly` |
| `agent:dr-voss-thorne` | `flair` |

---

## How to Enable

```bash
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

Then call `render_agent_voice(agent_id, text, output_path)` or use `VoiceAdapter` directly.

---

## Follow-ups for Namshub

- [ ] Review and merge PR #8 (primary) — `feature/voicedna-openclaw-per-agent-voices`
- [ ] Decide fate of PR #7 (`feature/voicedna-openclaw-integration`) — similar scope; may close as superseded
- [ ] Wire `render_agent_voice()` into the live OpenClaw TTS pipeline (currently wired via env-opt-in only)
- [ ] Add companion changes in `lukejmorrison/openclaw` repo once PR #8 merges
- [ ] Validate WAV output quality with real TTS backend (current demo uses SimpleLocalTTS stub)
