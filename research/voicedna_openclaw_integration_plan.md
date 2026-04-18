# VoiceDNA ↔ OpenClaw integration plan

**Branch validated:** `feature/voicedna-openclaw-integration`  
**Pilot status:** opt-in, additive, local-first

## Validation results
- `python -m pytest tests/test_voice_adapter.py -v` → **18 passed**
- `python -m pytest` → **46 passed**
- `python examples/openclaw_voicedemo.py` → produced:
  - `examples/openclaw/output/namshub_neutral.wav` — 164,696 bytes, mono, 22,050 Hz
  - `examples/openclaw/output/david_friendly.wav` — 211,876 bytes, mono, 22,050 Hz
  - `examples/openclaw/output/voss_flair.wav` — 209,542 bytes, mono, 22,050 Hz

## What to wire where

### VoiceDNA side (already present on this branch)
- `voicedna/openclaw_adapter.py:121-145` — `VOICEDNA_OPENCLAW_PRESETS_MAP` JSON loader
- `voicedna/openclaw_adapter.py:166-283` — `VoiceAdapter` preset selection + synthesis
- `voicedna/openclaw_live_voice.py:37-65` — default agent→preset map + singleton adapter merge
- `voicedna/openclaw_live_voice.py:68-95` — `render_agent_voice(...)` entry point to call from OpenClaw

### OpenClaw runtime seam
Use the live TTS path, not the demo path:
- `/home/namshub/dev/openclaw/openclaw.sh:1893-1897` — CLI dispatch to `audio-tts-reply`
- `/home/namshub/dev/openclaw/skills/audio-responder-tts/audio_tts_reply.sh:78-116` — current agent→voice selection block; replace/wrap this seam with the VoiceDNA adapter call
- `/home/namshub/dev/openclaw/skills/audio-responder-tts/SKILL.md:15-20, 51-56` — policy text for outbound voice replies; update only after the hook exists
- `/home/namshub/dev/VoiceDNA/examples/openclaw/voicedna_tts_hook.py:73-107` — registration patterns to copy into an OpenClaw skill/plugin

## Minimal opt-in wiring example

```python
# OpenClaw-side Python shim (new small helper or skill plugin)
import os
from voicedna.openclaw_live_voice import render_agent_voice


def render_agent_tts(text: str, agent_id: str, agent_name: str | None = None, output_path: str | None = None) -> bytes:
    # Preserve current behavior unless explicitly enabled.
    if os.getenv("VOICEDNA_OPENCLAW_PRESETS") != "1":
        return fallback_existing_tts(text, output_path=output_path)

    return render_agent_voice(
        text=text,
        agent_id=agent_id,
        agent_name=agent_name,
        output_path=output_path,
    )
```

If the existing OpenClaw hook expects a post-processor, use the same pattern as `examples/openclaw/voicedna_tts_hook.py` and wrap the current TTS provider rather than changing its default provider.

## Step-by-step implementation tasks for Dr Voss
1. Add a tiny OpenClaw shim that imports `render_agent_voice` and is only enabled when `VOICEDNA_OPENCLAW_PRESETS=1`.
2. Wire that shim into the live outbound TTS seam (`audio_tts_reply.sh` or the equivalent Python skill/plugin) so agent id/name reaches the adapter.
3. Keep the current voice path as fallback when the env flag or mapping is absent.
4. Load per-agent preset mapping from `VOICEDNA_OPENCLAW_PRESETS_MAP` and keep the three pilot presets only: `neutral`, `friendly`, `flair`.
5. Add or extend integration tests for the live shim and keep the existing adapter tests untouched.
6. Re-run the repo test suite and the demo in a backend-complete environment before merge.
7. Update docs/skill text after the runtime hook is proven, not before.

## Required env vars
- `VOICEDNA_OPENCLAW_PRESETS=1` — opt-in signal; must not change default behavior
- `VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'` — agent→preset routing map

## Reproduction commands
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -v
python -m pytest
python examples/openclaw_voicedemo.py
```

Optional live-hook smoke check:
```bash
python -m pytest tests/test_openclaw_live_voice.py -v
```

## CI considerations
- Run adapter tests and live-hook tests in normal CI.
- Treat the demo as a separate job or optional smoke check if the VoiceDNA backend is not always available.
- Keep synthesis tests gated so they skip cleanly when `voice_dna` / backend deps are missing.
- Do **not** add or modify GitHub Actions workflow files in this task.
- If future pushes are blocked by GitHub permissions on workflow-related changes, use a PAT with `workflow` scope or ship a git bundle; do not try to bypass the restriction.

## Prioritized checklist for Dr Voss
- [ ] Wire the OpenClaw TTS seam to `render_agent_voice(...)` behind `VOICEDNA_OPENCLAW_PRESETS=1`
- [ ] Preserve fallback behavior when the env var or map is missing
- [ ] Keep `VOICEDNA_OPENCLAW_PRESETS_MAP` as the only routing config path
- [ ] Add/extend tests for the live shim and the agent routing map
- [ ] Re-run `python -m pytest` and `python examples/openclaw_voicedemo.py`
- [ ] Verify the generated WAVs are non-empty and valid before any PR/push
- [ ] Keep the feature opt-in; do not make VoiceDNA the default voice path
