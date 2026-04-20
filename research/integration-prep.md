# VoiceDNA × OpenClaw integration prep

Scope: prepare the per-agent VoiceAdapter wiring, keep the demo local-first, and provide reproducible smoke checks for generated WAV output.

## What this covers
- Local build / test commands
- CI commands
- Required env var names only
- Required secrets / permissions names only
- Verification steps for WAV output
- Blockers / approvals to request from Luke only if needed

## Assumptions
- Repo root: `/home/namshub/dev/VoiceDNA`
- The pilot stays additive and opt-in.
- The demo and validation can run without cloud services.
- If the full VoiceDNA synthesis backend is unavailable, the provided validation script still generates and validates a demo WAV locally.

## Local commands

### 1) Set up an editable dev install
```bash
cd /home/namshub/dev/VoiceDNA
python -m pip install -e ".[dev]"
```

### 2) Run the VoiceAdapter tests
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -q
```

### 3) Run the OpenClaw live-voice checks
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_openclaw_live_voice.py -q
```

### 4) Run the demo script
```bash
cd /home/namshub/dev/VoiceDNA
VOICEDNA_OPENCLAW_PRESETS=1 \
VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}' \
PYTHONPATH=. \
python examples/openclaw_voicedemo.py
```

### 5) Run the WAV validation script
```bash
cd /home/namshub/dev/VoiceDNA
bash research/test_tts.sh
```

### 6) Full local smoke pass
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py tests/test_openclaw_live_voice.py -q
bash research/test_tts.sh
```

## CI commands

Recommended CI job steps:

```bash
python -m pip install -e ".[dev]"
python -m pytest tests/test_voice_adapter.py tests/test_openclaw_live_voice.py -q
bash research/test_tts.sh
```

If the CI runner does not install the package in editable mode, set:

```bash
PYTHONPATH=.
```

## Required environment variables
Names only:
- `VOICEDNA_OPENCLAW_PRESETS`
- `VOICEDNA_OPENCLAW_PRESETS_MAP`
- `PYTHONPATH` (only if not using editable install)

## Required secrets / permissions
Names only:
- `GITHUB_TOKEN` or a GitHub PAT for push/PR automation, if Luke wants the branch pushed from a machine that does not already have Git auth
- GitHub permissions: `contents:write`, `pull_requests:write`
- `workflow` only if future changes touch `.github/workflows/*`

## Verification steps
1. Confirm the adapter contract:
   - `select_preset(agent_id, agent_name=None)` resolves `agent_id -> agent_name -> default`
   - `synthesize(text, preset, output_path=None)` returns WAV bytes and can write to disk
2. Run the demo script and confirm output files appear under:
   - `examples/openclaw/output/`
3. Validate the generated WAVs:
   - header magic: `RIFF....WAVE`
   - sample rate: `22050` Hz
   - bit depth: `16-bit` (`sampwidth == 2`)
   - mono channel count
4. Run the validation script and confirm it exits with status `0`.
5. Run the pytest suite for the adapter and live-voice checks.

## Blockers / approvals needed
- No blocker for the prep docs or validation script itself.
- Ask Luke only if a push/PR flow is needed and Git auth is not already configured:
  - approve a GitHub PAT or token with `contents:write` and `pull_requests:write`
- Ask Luke for `workflow` only if future work touches `.github/workflows/*`.
- No cloud secret is required for the local demo path.
