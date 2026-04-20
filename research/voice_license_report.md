# VoiceDNA preset / license compatibility notes

## Verdict
No blocker found for the OpenClaw per-agent voice pilot.

## Why
- VoiceDNA `pyproject.toml` declares the project under the MIT license.
- The pilot uses only the built-in preset names: `neutral`, `friendly`, and `flair`.
- I did not find evidence in the repository of a bundled third-party voice asset that would obviously block redistribution of the code changes.

## Practical compatibility notes
- Treat generated demo WAVs as artifacts, not as proof that any third-party voice asset can be redistributed.
- If future presets depend on external sample packs, proprietary models, or licensed voice data, document the provenance and redistribution rights before shipping.
- Keep the feature opt-in so license or asset concerns do not affect default VoiceDNA behavior.

## Current implementation stance
- Code path is additive and local-first.
- No cloud service is required for the demo path.
- No new license obligation was identified for the current pilot docs.

## References
- `/home/namshub/dev/VoiceDNA/pyproject.toml`
- `/home/namshub/dev/VoiceDNA/LICENSE`
- `/home/namshub/dev/VoiceDNA/voicedna/openclaw_adapter.py`
- `/home/namshub/dev/VoiceDNA/examples/openclaw_voicedemo.py`
