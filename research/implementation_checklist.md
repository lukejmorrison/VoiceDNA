# VoiceDNA → OpenClaw Implementation Checklist

Branch: `feature/voicedna-openclaw-per-agent-voices`

## Scope
- Keep the pilot additive and opt-in.
- Do **not** change default VoiceDNA behavior.
- Use the existing `VoiceAdapter` + OpenClaw hook path; no new secrets.
- Prefer local verification before any PR/push.

## Checklist for Dr Voss

### 1) Confirm the repo state and exact integration files
- [ ] Verify VoiceDNA and OpenClaw branches are correct.
- [ ] Confirm the integration already exists in the expected files.
- [ ] Only touch the narrowest files needed for rollout/docs/CI.

Useful commands:
```bash
cd /home/namshub/dev/VoiceDNA
git status --short --branch
git branch --show-current

cd /home/namshub/dev/openclaw
git status --short --branch
git branch --show-current
```

Expected VoiceDNA files:
- `voicedna/openclaw_adapter.py`
- `examples/openclaw_voicedemo.py`
- `tests/test_voice_adapter.py`
- `tests/test_openclaw_live_voice.py`

Expected OpenClaw files:
- `tools/voicedna_adapter.py`
- `tools/voicedna_tts_hook.py`
- `tests/test_voicedna_adapter.py`
- `tests/test_voicedna_tts_hook.py`
- `tests/test_voicedna_e2e.py`
- `README.md`
- `.github/workflows/ci.yml` only if CI should exercise the integration explicitly
- `skills/voicedna-agent-voices/SKILL.md` if docs need syncing

### 2) Validate the adapter contract in VoiceDNA
- [ ] Confirm preset selection order is `agent_id` → `agent_name` → default.
- [ ] Confirm the built-in presets are exactly `neutral`, `friendly`, `flair`.
- [ ] Confirm synthesis returns non-empty WAV bytes and can write to disk.

Run:
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -v
python -m pytest tests/test_openclaw_live_voice.py -v
```

If you need a quick smoke run of the demo:
```bash
cd /home/namshub/dev/VoiceDNA
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
file examples/openclaw/output/*.wav
python - <<'PY'
from pathlib import Path
import wave
root = Path('/home/namshub/dev/VoiceDNA/examples/openclaw/output')
for p in sorted(root.glob('*.wav')):
    with wave.open(str(p), 'rb') as w:
        print(p.name, w.getnchannels(), w.getframerate(), w.getsampwidth(), w.getnframes())
        assert w.getnchannels() == 1
        assert w.getframerate() == 22050
        assert w.getsampwidth() == 2
PY
```

### 3) Validate the OpenClaw shim and hook
- [ ] Confirm the shim is opt-in only.
- [ ] Confirm `VOICEDNA_OPENCLAW_PRESETS` disabled means no behavior change.
- [ ] Confirm the hook returns `None` cleanly when disabled or unavailable.
- [ ] Confirm agent IDs map to the intended presets.

Run:
```bash
cd /home/namshub/dev/openclaw
python -m pytest tests/test_voicedna_adapter.py -v
python -m pytest tests/test_voicedna_tts_hook.py -v
python -m pytest tests/test_voicedna_e2e.py -v
```

### 4) Verify local demo artifacts exist and are reviewer-ready
- [ ] Generate three WAVs under `examples/openclaw/output/`.
- [ ] Ensure they are non-empty and valid RIFF/WAVE files.
- [ ] Copy reviewer artifacts into the shared handoff area if needed.

Reviewer copy path:
```bash
mkdir -p /home/namshub/.openclaw/workspaces/namshub/artifacts/voicedna-demo
cp /home/namshub/dev/VoiceDNA/examples/openclaw/output/*.wav \
  /home/namshub/.openclaw/workspaces/namshub/artifacts/voicedna-demo/
```

### 5) Keep rollout opt-in and reversible
- [ ] Ensure the env gate is the only activation path.
- [ ] Default behavior must remain unchanged when env vars are unset.
- [ ] Rollback is just unsetting env vars and removing any live hook call site if one was added.

Activation example:
```bash
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

### 6) Prepare PR/bundle handoff, but do not push without approval
- [ ] If a bundle is needed, create it locally.
- [ ] If a push/PR is needed, verify PAT scope first.
- [ ] Do not create or use secrets in the repo.

Suggested bundle path:
```bash
tmp_bundle=/tmp/feat-voicedna-openclaw.bundle
```

### 7) Update docs only if they’re stale
- [ ] Sync the OpenClaw README if it still describes the demo/output path inaccurately.
- [ ] Sync the VoiceDNA/OpenClaw skill card only if it lags the actual hook path.
- [ ] Keep documentation factual and short.

### 8) Record the implementation decision
- [ ] Keep the feature additive, local-first, and opt-in.
- [ ] Do not expand the scope to unrelated TTS paths unless the agent identity is already present there.
- [ ] Preserve the current preset names and public behavior.

## Recommended execution order
1. Run the VoiceDNA tests.
2. Run the OpenClaw shim/hook tests.
3. Generate and validate the three demo WAVs.
4. Stage reviewer artifacts if requested.
5. Prepare the PR body or bundle notes.

## Minimal dependency notes
- No new runtime dependency should be required for the current pilot path.
- If CI needs to import VoiceDNA, the runner must check out or install the VoiceDNA repo first.
- Keep the existing preset set only: `neutral`, `friendly`, `flair`.

## Handoff summary for Dr Voss
- Treat the pilot as already implemented and focus on verification, docs, and rollout hygiene.
- The narrow integration surface is the OpenClaw TTS boundary (`tools/voicedna_tts_hook.py`) plus the shim (`tools/voicedna_adapter.py`).
- Keep all changes reversible with env vars.
