Title: Per-agent OpenClaw voice presets — feature/voicedna-openclaw-per-agent-voices

Body:
This PR introduces an OpenClaw adapter (voicedna.openclaw_adapter) to route per-agent VoiceDNA presets and a demo for generating per-agent WAVs.

Verification performed:
- Checked out branch feature/voicedna-openclaw-per-agent-voices.
- Ran pytest; collection failed due to missing runtime dependency 'voice_dna'.
- Lint and build steps were not applicable (project is Python-based; no package.json).
- Demo generation not run because the VoiceDNA core package is missing.

Short changelog:
- Add voicedna/openclaw_adapter.py implementing VoiceAdapter + preset registry.
- Add examples/openclaw_voicedemo.py (demo script).
- Add unit tests covering preset selection and synthesis smoke tests.

Action required from maintainer to complete verification:
1) Install or make importable the 'voice_dna' package (e.g. `pip install -e /path/to/voice_dna` or `export PYTHONPATH=/path/to/voice_dna:$PYTHONPATH`) so pytest can import VoiceDNA.
2) Re-run: `python -m pytest tests/test_voice_adapter.py -v`, `python -m pytest`, and `python examples/openclaw_voicedemo.py` to regenerate the demo WAVs.
3) No secrets are required for the local demo/test path; the only missing prerequisite is the importable `voice_dna` package.

If push to remote is blocked for you, create and apply the bundle locally with:

  git bundle create /tmp/voicedna_pr_bundle.bundle HEAD
  # then transfer and fetch/apply on remote machine:
  git clone /tmp/voicedna_pr_bundle.bundle -b feature/voicedna-openclaw-per-agent-voices <destination-dir>

(Do NOT push from this agent without explicit PAT and approval.)
