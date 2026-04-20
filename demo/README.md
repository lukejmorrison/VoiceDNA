# VoiceDNA Per-Agent Voice Demo

Demo WAV artifacts for the OpenClaw per-agent voice pilot (v3.1.0).

## Files

| File | Agent | Preset | Text |
|------|-------|--------|------|
| `namshub_neutral.wav` | agent:namshub | neutral | "Hello. I am Namshub, your primary orchestration agent." |
| `david_friendly.wav` | agent:david-hardman | friendly | "Hey there! David Hardman here — happy to help with anything you need today." |
| `voss_flair.wav` | agent:dr-voss-thorne | flair | "Greetings. Dr Voss Thorne. Precision is the only acceptable standard." |

## How to regenerate

```bash
cd /path/to/VoiceDNA
python examples/openclaw_voicedemo.py
cp examples/openclaw/output/*.wav demo/
```

## Verification Checklist

- [x] `namshub_neutral.wav` — non-zero bytes, audible speech
- [x] `david_friendly.wav` — non-zero bytes, audible speech
- [x] `voss_flair.wav` — non-zero bytes, audible speech
- [x] All three presets are distinct (different pitch/rate parameters)
- [x] No synthesis errors during generation
