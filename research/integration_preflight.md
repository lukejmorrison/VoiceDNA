# VoiceDNA v3.1.1 → OpenClaw per-agent voice preflight

**Goal:** wire `VoiceDNA` `VoiceAdapter` into the live OpenClaw TTS path with the smallest possible blast radius.

**Release anchor:** VoiceDNA `v3.1.1` (`69d8d0c`)
**OpenClaw branch for the live seam:** `feat/voicedna-openclaw-integration`
**Rollout style:** opt-in, additive, reversible

## 1) What changes are actually needed

- **No schema or data migrations.** This pilot is env-gated and file-level only.
- **OpenClaw needs a small live seam** that calls `voicedna.openclaw_live_voice.render_agent_voice(...)` (or the local shim in `tools/voicedna_adapter.py`) when enabled.
- **Default behavior must stay unchanged** when the feature flag is absent.
- **No GitHub Actions workflow edits** are required for this rollout.

## 2) Exact rollout steps

### Step A — Verify the VoiceDNA release anchor

```bash
cd /home/namshub/dev/VoiceDNA
git describe --tags --exact-match 69d8d0c
python -m pytest tests/test_voice_adapter.py -v
python -m pytest tests/test_openclaw_live_voice.py -v
```

Expected:
- `git describe` prints `v3.1.1`
- targeted VoiceDNA tests pass

### Step B — Prepare the OpenClaw runtime path

OpenClaw reads its environment from `OPENCLAW_ENV_FILE` (default: `/home/namshub/dev/openclaw/.openclaw.env`).

Add or confirm these lines in that file:

```bash
VOICEDNA_OPENCLAW_PRESETS=1
VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

If you are using a systemd user service, make the same env values available to the service process before restart.

### Step C — Install/refresh the VoiceDNA runtime on the OpenClaw host

```bash
cd /home/namshub/dev/openclaw
./openclaw.sh voice-dna-setup
./openclaw.sh voice-dna-validate namshub --strict
./openclaw.sh voice-dna-env namshub
```

Expected:
- OpenClaw’s VoiceDNA venv is created/refreshed
- the registry resolves the expected per-agent env names
- VoiceDNA paths point at the local VoiceDNA checkout

### Step D — Wire the live TTS seam

Use the existing OpenClaw live TTS entry point:

- `skills/audio-responder-tts/audio_tts_reply.sh`
- `tools/voicedna_adapter.py`

Behavior to preserve:

- When `VOICEDNA_OPENCLAW_PRESETS` is unset/false, keep the current TTS path unchanged.
- When the flag is `1`, call the VoiceDNA adapter and route by `agent_id` → `agent_name` → default preset.
- Keep the preset map limited to `neutral`, `friendly`, and `flair` for the pilot.

### Step E — Restart and smoke test

```bash
systemctl --user restart openclaw-gateway.service
journalctl --user -u openclaw-gateway.service --since "5 minutes ago" --no-pager | tail -50
```

Then run the runtime checks:

```bash
cd /home/namshub/dev/openclaw
python -m pytest tests/test_voicedna_adapter.py -v

cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -v
python -m pytest tests/test_openclaw_live_voice.py -v
python -m pytest -q
ruff check voicedna/openclaw_adapter.py voicedna/openclaw_live_voice.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py tests/test_openclaw_live_voice.py
python -m py_compile voicedna/openclaw_adapter.py voicedna/openclaw_live_voice.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py tests/test_openclaw_live_voice.py
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
```

Expected demo outputs:

- `examples/openclaw/output/namshub_neutral.wav`
- `examples/openclaw/output/david_friendly.wav`
- `examples/openclaw/output/voss_flair.wav`

## 3) Rollback steps

1. Unset the feature flag and preset map in the OpenClaw env file.
2. Restart the OpenClaw service.
3. Revert the seam import/hook if it was merged.
4. Confirm the default TTS path works again with the flag disabled.

```bash
unset VOICEDNA_OPENCLAW_PRESETS
unset VOICEDNA_OPENCLAW_PRESETS_MAP
systemctl --user restart openclaw-gateway.service
```

## 4) Required permissions and secrets

### Required for the pilot rollout itself
- **None.** The live per-agent preset path does not require deploy keys or service-account credentials.
- **No new secrets** are introduced by the preset-routing pilot.

### Required if you need to push the OpenClaw PR from a token
- **`contents:write`** — push the branch
- **`pull_requests:write`** — create/update the PR with `gh` or the API
- **`workflow`** — only if a future revision touches `.github/workflows/*`

### How to obtain/apply them safely
- Create the token in GitHub settings with the minimum scopes above.
- Store it in a password manager or another secret store, not in chat.
- Use it only in the shell/session that needs it:

```bash
export GITHUB_TOKEN="<paste-from-secret-store>"
# or
printf '%s' "$GITHUB_TOKEN" | gh auth login --with-token
```

### Optional VoiceDNA registry secrets
If the team later decides to use the encrypted `.voicedna.enc` registry path instead of the preset pilot, obtain the existing `VOICEDNA_PASSWORD_*` values from the team secret store and export them in the OpenClaw env file. Do **not** paste those values into chat.

## 5) Bottom line

- **Migrations:** none
- **Feature flags:** `VOICEDNA_OPENCLAW_PRESETS=1` + optional `VOICEDNA_OPENCLAW_PRESETS_MAP`
- **Workflow-file permission:** not required for this rollout
- **Rollback:** simple env unset + service restart