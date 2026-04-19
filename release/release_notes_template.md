# VoiceDNA release notes template — OpenClaw per-agent voices

## Summary
Add a short paragraph describing the pilot and the user-facing effect.

## Highlights
- Opt-in per-agent voice preset routing for OpenClaw.
- Three presets supported in the pilot: `neutral`, `friendly`, `flair`.
- Local-first demo produces WAV outputs for review.

## Verification
- `python -m pytest tests/test_voice_adapter.py -v`
- `python -m pytest tests/test_openclaw_live_voice.py -v`
- Optional lint check: `ruff check .`

## Artifacts
- `examples/openclaw/output/namshub_neutral.wav`
- `examples/openclaw/output/david_friendly.wav`
- `examples/openclaw/output/voss_flair.wav`

## Notes
- No `.github/workflows/*` files were changed.
- Feature is opt-in and does not alter default VoiceDNA behavior.
