# VoiceDNA → OpenClaw live voice pipeline integration plan

**Goal:** wire `voicedna.openclaw_adapter.VoiceAdapter` into the live OpenClaw agent voice path in a way that is additive, opt-in, and easy to roll back.

**Status:** planning doc for the next milestone. No push/PR is assumed.

---

## 1) Current facts and recommended integration shape

### Already present in VoiceDNA
- `voicedna/openclaw_adapter.py`
  - per-agent preset selection
  - preset registry: `neutral`, `friendly`, `flair`
  - env loader: `VOICEDNA_OPENCLAW_PRESETS_MAP`
  - runtime registration helpers
- `voicedna/openclaw_live_voice.py`
  - live adapter entry point: `render_agent_voice(...)`
  - default OpenClaw persona map
- `examples/openclaw_voicedemo.py`
  - local reproducible WAV demo
- `tests/test_voice_adapter.py`
  - adapter unit coverage
- `tests/test_openclaw_live_voice.py`
  - live adapter smoke/integration coverage

### Already present in OpenClaw
- `tools/voicedna_adapter.py`
  - opt-in shim that returns `None` unless `VOICEDNA_OPENCLAW_PRESETS=1`
  - default mapping for the three pilot agents
- `skills/audio-responder-tts/audio_tts_reply.sh`
  - current live outbound TTS seam
- `skills/audio-responder-tts/SKILL.md`
  - user-facing documentation for voice replies
- `openclaw.sh`
  - dispatch entry for `audio-tts-reply`

### Recommended shape
Use the existing OpenClaw shim as the opt-in gate and keep the default path unchanged:

1. OpenClaw continues to call the current TTS pipeline by default.
2. When `VOICEDNA_OPENCLAW_PRESETS=1`, OpenClaw resolves an agent preset map.
3. The live voice seam routes through `VoiceAdapter`/`render_agent_voice(...)`.
4. If the feature flag is off or VoiceDNA is unavailable, fall back to the current OpenClaw TTS path.

This keeps the change minimal, reversible, and compatible with current behavior.

---

## 2) Exact file-level change candidates in OpenClaw

> These are the concrete files most likely to change. Keep the diff small.

### A. `tools/voicedna_adapter.py`
**Purpose:** maintain the opt-in gate and preset map building.

Suggested small refinement:
- keep the env flag as the only enable switch
- keep the default map aligned with the pilot personas
- ensure unknown presets fail closed or are skipped with a warning

Possible snippet:
```python
if not is_voicedna_enabled():
    return None

preset_map = _build_preset_map()
adapter = VoiceAdapter(agent_presets=preset_map)
```

If a future refactor is needed, prefer **one** adapter constructor path and **one** mapping source of truth.

---

### B. `skills/audio-responder-tts/audio_tts_reply.sh`
**Purpose:** route the live reply through VoiceDNA when enabled.

Minimal change pattern:
- preserve current CLI args and default outputs
- detect the VoiceDNA opt-in flag
- if enabled, call the Python shim or `render_agent_voice(...)`
- otherwise keep the current binary/provider path

Example decision branch:
```bash
if [[ "${VOICEDNA_OPENCLAW_PRESETS:-}" == "1" ]]; then
  # Use VoiceDNA live routing
  # agent id/name must be passed through here
else
  # Keep existing provider selection
fi
```

If the script is easier to preserve as-is, add a tiny Python bridge instead of rewriting the shell logic.

---

### C. `skills/audio-responder-tts/SKILL.md`
**Purpose:** document the opt-in live voice behavior and the fallback.

Update only after the seam is proven.

Add notes for:
- `VOICEDNA_OPENCLAW_PRESETS=1`
- `VOICEDNA_OPENCLAW_PRESETS_MAP=...`
- fallback behavior when either is missing
- the three pilot personas and their preset names

---

### D. `tests/test_voicedna_adapter.py`
**Purpose:** protect the OpenClaw shim behavior.

Add or keep tests for:
- env flag off → `None`
- env flag on + importable VoiceDNA → adapter returned
- preset map defaults to the three pilot mappings
- custom env map overrides defaults
- invalid JSON fails safely
- cached singleton reset works

---

### E. `tests/test_openclaw_live_voice.py`
**Purpose:** verify the live routing path in the VoiceDNA repo remains correct.

Keep coverage for:
- known agent ids
- agent-name alias fallback
- output file writing
- deterministic mapping order

---

### F. `openclaw.sh` (only if dispatch needs a small pass-through)
**Purpose:** forward any new args or env that the seam needs.

Only change this if the live seam needs additional routing context. Otherwise leave it alone.

---

## 3) Required config keys and env vars

### OpenClaw runtime env
- `VOICEDNA_OPENCLAW_PRESETS=1`
  - turns the feature on
  - absence means default OpenClaw behavior
- `VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'`
  - optional JSON map
  - can override defaults for local experiments

### Future encrypted VoiceDNA routing only if the team later chooses it
- `VOICEDNA_PASSWORD_*`
- `VOICEDNA_ENC_PATH`

These are **not** required for the current preset pilot.
Do **not** store passwords or `.voicedna.enc` contents in plaintext.

---

## 4) Step-by-step implementation plan

### Step 1 — Keep the opt-in gate explicit
- Ensure the OpenClaw shim only activates when `VOICEDNA_OPENCLAW_PRESETS=1`.
- Confirm the default path returns the existing non-VoiceDNA behavior.

Verification:
```bash
cd /home/namshub/dev/openclaw
python -m pytest tests/test_voicedna_adapter.py -v
```

---

### Step 2 — Pass the agent identity into the live voice seam
- The live TTS seam must receive `agent_id` and, if available, `agent_name`.
- Do not infer persona from text content.
- Preserve deterministic resolution order: `agent_id` → `agent_name` → default preset.

If the seam currently only receives text, add a minimal argument pass-through rather than changing the selection logic.

---

### Step 3 — Route through VoiceDNA only when enabled
- In the live seam, call the VoiceDNA adapter path only when the flag is set.
- Otherwise, invoke the current OpenClaw TTS provider unchanged.
- Keep fallback behavior identical for non-VoiceDNA users.

Recommended pattern:
```python
adapter = get_voice_adapter()
if adapter is None:
    return fallback_tts(text, output_path=output_path)
return render_agent_voice(text=text, agent_id=agent_id, agent_name=agent_name, output_path=output_path)
```

---

### Step 4 — Keep the preset map as the single source of truth
- Use the built-in pilot defaults:
  - `agent:namshub` → `neutral`
  - `agent:david-hardman` → `friendly`
  - `agent:dr-voss-thorne` → `flair`
- Allow `VOICEDNA_OPENCLAW_PRESETS_MAP` to override those defaults for local experiments.
- Reject or skip unknown preset names with a clear warning.

---

### Step 5 — Update docs only after the seam is proven
- Update `skills/audio-responder-tts/SKILL.md` with the new live voice option.
- Update `README.md` or a dedicated OpenClaw note only if the runtime hook is now real and tested.
- Keep docs aligned with the actual env var names and preset names.

---

### Step 6 — Add or refresh tests
- OpenClaw shim tests should cover the enable/disable gate and mapping behavior.
- VoiceDNA live tests should continue to validate the live adapter interface.
- If a shell seam is changed, add a focused integration smoke test around that seam.

---

### Step 7 — Validate in a backend-complete environment
Run the VoiceDNA test suite and demo again in an environment that actually has the runtime backend installed.

Suggested sequence:
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -v
python -m pytest tests/test_openclaw_live_voice.py -v
python -m pytest -q
VOICEDNA_OPENCLAW_PRESETS=1 python examples/openclaw_voicedemo.py
```

---

## 5) Reproducible local test plan

### A. VoiceDNA unit and integration checks
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -v
python -m pytest tests/test_openclaw_live_voice.py -v
python -m pytest -q
python -m py_compile voicedna/openclaw_adapter.py voicedna/openclaw_live_voice.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py tests/test_openclaw_live_voice.py
```

### B. Demo WAV generation
```bash
cd /home/namshub/dev/VoiceDNA
VOICEDNA_OPENCLAW_PRESETS=1 python examples/openclaw_voicedemo.py
stat -c '%n %s bytes' examples/openclaw/output/*.wav
```

Expected files:
- `examples/openclaw/output/namshub_neutral.wav`
- `examples/openclaw/output/david_friendly.wav`
- `examples/openclaw/output/voss_flair.wav`

### C. OpenClaw shim tests
```bash
cd /home/namshub/dev/openclaw
python -m pytest tests/test_voicedna_adapter.py -v
```

### D. Live seam smoke test after wiring
Once `audio_tts_reply.sh` is patched to call the adapter, run something like:
```bash
cd /home/namshub/dev/openclaw
VOICEDNA_OPENCLAW_PRESETS=1 \
VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}' \
./openclaw.sh audio-tts-reply "Hello from Namshub" --voice namshub --output /tmp/namshub.wav

VOICEDNA_OPENCLAW_PRESETS=1 \
VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}' \
./openclaw.sh audio-tts-reply "Hello from David" --voice david-hardman --output /tmp/david.wav

VOICEDNA_OPENCLAW_PRESETS=1 \
VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}' \
./openclaw.sh audio-tts-reply "Hello from Voss" --voice dr-voss-thorne --output /tmp/voss.wav
```

Then validate:
```bash
file /tmp/namshub.wav /tmp/david.wav /tmp/voss.wav
stat -c '%n %s bytes' /tmp/namshub.wav /tmp/david.wav /tmp/voss.wav
```

---

## 6) Approvals, credentials, and secret handling

### Approvals likely needed
- No special approval is required for the preset pilot itself if only code/docs are changed.
- If the team later modifies `.github/workflows/*`, GitHub may require a PAT with `workflow` scope or equivalent repo permissions.
- If the live seam touches protected deployment paths, ask for the repo’s normal branch/PR approval flow.

### Credentials
- None required for the current preset pilot.
- If encrypted `.voicedna.enc` files are ever wired into the live path, use the team secret store or environment injection.
- Never commit passwords, API keys, or decrypted voice artifacts.

---

## 7) Safe rollback plan

Rollback should be one of the easiest parts of this rollout.

1. Unset `VOICEDNA_OPENCLAW_PRESETS`.
2. Unset `VOICEDNA_OPENCLAW_PRESETS_MAP`.
3. Restart the OpenClaw service or reload the shell/session.
4. Confirm the original TTS path is active.
5. Revert the seam patch if the integration needs to be backed out.

Because the feature is opt-in, rollback should restore the previous behavior with no data migration.

---

## 8) PR outline ready for review

### Branch
- `feature/voicedna-openclaw-live-seam`

### Suggested commits
1. `chore(openclaw): add opt-in VoiceDNA live voice shim`
2. `test(openclaw): cover VoiceDNA shim and live seam`
3. `docs(openclaw): document VoiceDNA live voice opt-in`

### Patch shape
- Keep the OpenClaw change set minimal.
- Do not add workflow files unless there is a separate CI reason.
- Keep the VoiceDNA repo changes additive and backwards compatible.

### Likely diff list
- `tools/voicedna_adapter.py`
- `skills/audio-responder-tts/audio_tts_reply.sh`
- `skills/audio-responder-tts/SKILL.md`
- `tests/test_voicedna_adapter.py`
- `tests/test_openclaw_live_voice.py` only if a new seam test is needed in OpenClaw

---

## 9) Go/no-go checklist

- [ ] Live seam preserves current behavior when `VOICEDNA_OPENCLAW_PRESETS` is unset
- [ ] VoiceDNA adapter returns the correct preset for each pilot agent
- [ ] Unknown preset names are rejected or skipped safely
- [ ] Demo WAVs are generated and non-empty
- [ ] OpenClaw shim tests pass
- [ ] Live seam smoke test passes in a backend-complete environment
- [ ] No secrets are checked in
- [ ] No `.github/workflows/*` files changed unless explicitly approved

---

## 10) Short conclusion

The safest path is to keep the current OpenClaw TTS flow intact and gate VoiceDNA routing behind a single env var. Use `render_agent_voice(...)` only in the live outbound seam, preserve fallback behavior, and validate with both unit tests and WAV-producing smoke tests before rollout.
