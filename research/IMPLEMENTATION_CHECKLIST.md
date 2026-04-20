# VoiceDNA → OpenClaw implementation checklist

- Branch: `feature/voicedna-openclaw-per-agent-voices`
- Confirm VoiceDNA repo root is the source of truth: `/home/namshub/dev/VoiceDNA`
- Confirm OpenClaw shim/references are in `/home/luke/dev/openclaw` via symlinked workspace path
- Keep the feature opt-in behind `VOICEDNA_OPENCLAW_PRESETS=1`
- Preserve the default fallback mapping:
  - `agent:namshub` → `neutral`
  - `agent:david-hardman` → `friendly`
  - `agent:dr-voss-thorne` → `flair`

## Files to edit or verify

### VoiceDNA
- `voicedna/openclaw_adapter.py`
- `examples/openclaw_voicedemo.py`
- `tests/test_voice_adapter.py`
- `tests/test_openclaw_live_voice.py`
- `README.md`
- `pyproject.toml` only if deps or test markers change

### OpenClaw
- `tools/voicedna_adapter.py`
- `tools/voicedna_registry.py`
- `skills/voicedna-agent-voices/SKILL.md`
- `skills/voice-dna-registry/registry.json`
- `docs/voicedna-integration.md`
- `tests/test_voicedna_adapter.py`
- `tests/test_voicedna_e2e.py`

## Concrete implementation steps for Dr Voss

1. Wire the shim into the OpenClaw voice path only when `VOICEDNA_OPENCLAW_PRESETS=1` is set.
2. Keep the adapter lazy-loaded so normal OpenClaw startup cost stays unchanged.
3. Use the existing `VoiceAdapter` preset resolution order: exact agent ID → alias → default.
4. Keep the pilot preset map tiny and explicit; no remote config service.
5. Preserve local-first synthesis and current WAV format expectations.
6. If any live OpenClaw code needs to call the shim, keep it behind a one-line helper so rollback is trivial.
7. Do not add a remote push or PR step until approval/PAT is available.

## Tests to run

### VoiceDNA
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -v
python -m pytest tests/test_openclaw_live_voice.py -v
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
```

### OpenClaw
```bash
cd /home/luke/dev/openclaw
python -m pytest tests/test_voicedna_adapter.py -v
python -m pytest tests/test_voicedna_e2e.py -v
python demo/voicedna_demo.py
```

## Demo commands

```bash
cd /home/namshub/dev/VoiceDNA
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
```

Expected outputs:
- `examples/openclaw/output/namshub_neutral.wav`
- `examples/openclaw/output/david_friendly.wav`
- `examples/openclaw/output/voss_flair.wav`

## Blockers / approvals

- No blocker for local docs or demo verification.
- If a push or PR is requested, a PAT may be required for GitHub workflow-file changes.
- No secrets should be stored in memory or written to repo files.
