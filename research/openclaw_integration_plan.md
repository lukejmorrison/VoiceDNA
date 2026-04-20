# VoiceDNA ↔ OpenClaw per-agent voice integration plan

**Purpose:** deployment-ready checklist for wiring VoiceDNA into the OpenClaw per-agent voice pipeline without changing default TTS behavior.

**Status:** additive, opt-in, local-first. Default OpenClaw behavior must remain unchanged unless the feature flag is enabled.

---

## 1) Required OpenClaw changes

> Keep the OpenClaw side narrow: only touch the TTS boundary and the tests/docs around it.

### 1.1 `tools/voicedna_adapter.py`
**Goal:** create a lazy VoiceDNA adapter factory and preset-map loader.

**Outline:**
- Add `is_voicedna_enabled()` behind `VOICEDNA_OPENCLAW_PRESETS`.
- Load preset overrides from `VOICEDNA_OPENCLAW_PRESETS_MAP`.
- Keep adapter creation lazy so the import cost is paid only when enabled.
- Expose a reset hook for tests.

### 1.2 `tools/voicedna_tts_hook.py` or the narrowest live TTS wrapper
**Goal:** route agent audio through VoiceDNA only when the agent identity is available and the feature flag is on.

**Outline:**
- Resolve `agent_id` first, then `agent_name`, then default preset.
- Call the VoiceDNA bridge before the existing TTS fallback.
- If the bridge returns `None`, continue through the current OpenClaw TTS path unchanged.
- Do not add routing to unrelated core paths.

### 1.3 `examples/openclaw/voicedna_tts_hook.py` or equivalent demo integration point
**Goal:** provide a runnable example of the live wrapper behavior.

**Outline:**
- Show how a speaker identity reaches the hook.
- Demonstrate opt-in routing with the default fallback preserved.
- Keep the sample local-only and no-cloud.

### 1.4 Tests in OpenClaw
**Goal:** prove the shim, gating, and end-to-end path are safe.

**Files:**
- `tests/test_voicedna_adapter.py`
- `tests/test_voicedna_e2e.py`

**Outline:**
- Feature flag off → returns `None` / no routing.
- Feature flag on → preset selection resolves in the expected order.
- Demo path produces valid WAV output when the backend is available.
- Backend absence skips synthesis tests instead of failing CI.

### 1.5 Documentation sync in OpenClaw
**Goal:** keep operational docs aligned with the opt-in design.

**Likely files:**
- `README.md`
- `VOICEDNA_RUNBOOK.md`
- `DESIGN_DOC_voicedna.md`
- `skills/voicedna-agent-voices/SKILL.md`

**Outline:**
- Document the env vars.
- State that the feature is additive and disabled by default.
- Note that no cloud secrets are required for the pilot.

---

## 2) Required VoiceDNA changes

> VoiceDNA already contains the core pilot files; keep changes limited and additive.

### 2.1 `voicedna/openclaw_adapter.py`
**Goal:** maintain the canonical adapter contract.

**Outline:**
- Preserve `select_preset(agent_id, agent_name=None)` fallback order:
  1. exact `agent_id`
  2. `agent_name` alias
  3. default preset (`neutral`)
- Preserve only the three pilot presets: `neutral`, `friendly`, `flair`.
- Keep runtime mapping support through `VOICEDNA_OPENCLAW_PRESETS_MAP`.

### 2.2 `voicedna/openclaw_live_voice.py`
**Goal:** remain the feature-flagged bridge into OpenClaw.

**Outline:**
- Return `None` when `VOICEDNA_OPENCLAW_PRESETS` is falsy.
- Keep the default VoiceDNA path unchanged when the opt-in flag is not set.
- Lazy-load any heavier synthesis dependencies.

### 2.3 `examples/openclaw_voicedemo.py`
**Goal:** keep a reproducible smoke test for the pilot.

**Outline:**
- Demonstrate the three pilot agents.
- Emit WAVs into `examples/openclaw/output/`.
- Make it obvious how to run the demo locally.

### 2.4 Tests in VoiceDNA
**Files:**
- `tests/test_voice_adapter.py`
- `tests/test_openclaw_live_voice.py`

**Outline:**
- Selection logic and env parsing.
- Feature-flag gating.
- Demo smoke / synthesis validation.

---

## 3) Env vars and config entries

### Required for the pilot
```bash
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

### Semantics
- `VOICEDNA_OPENCLAW_PRESETS` enables the bridge.
- `VOICEDNA_OPENCLAW_PRESETS_MAP` optionally overrides the agent→preset mapping.
- Resolution order remains `agent_id` → `agent_name` alias → default preset.

### Optional local VoiceDNA backend vars
These are not required to be documented as secrets in the plan, but may be needed by local synthesis environments:
- `VOICEDNA_PASSWORD`
- `VOICEDNA_ENC_PATH`
- `VOICEDNA_FORCE_AGE`

> Do not commit values for any secret-like env vars.

---

## 4) Local test plan

### 4.1 VoiceDNA unit and live-voice tests
From the VoiceDNA repo root:
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -q
python -m pytest tests/test_openclaw_live_voice.py -q
```

**Assert:**
- preset selection works
- env parsing works
- feature-flag-off path returns `None`
- synthesis paths are valid or skipped cleanly when dependencies are absent

### 4.2 Demo smoke test
```bash
cd /home/namshub/dev/VoiceDNA
VOICEDNA_OPENCLAW_PRESETS=1 \
VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}' \
PYTHONPATH=. \
python examples/openclaw_voicedemo.py
```

**Assert:**
- `examples/openclaw/output/namshub_neutral.wav`
- `examples/openclaw/output/david_friendly.wav`
- `examples/openclaw/output/voss_flair.wav`
- WAV files are non-empty and readable

### 4.3 WAV validation
```bash
file /home/namshub/dev/VoiceDNA/examples/openclaw/output/*.wav
python - <<'PY'
from pathlib import Path
import wave
root = Path('/home/namshub/dev/VoiceDNA/examples/openclaw/output')
for p in sorted(root.glob('*.wav')):
    with wave.open(str(p), 'rb') as w:
        print(p.name, w.getnchannels(), w.getframerate(), w.getsampwidth(), w.getnframes())
PY
```

**Assert:**
- files are RIFF/WAVE
- audio parameters are sane
- each file opens successfully with Python `wave`

---

## 5) CI test plan

### Recommended minimum CI coverage
- `python -m pytest tests/test_voice_adapter.py tests/test_openclaw_live_voice.py -q`
- OpenClaw shim tests that do not require a live synthesis backend should always run.

### CI expectations
- If the VoiceDNA synthesis backend is unavailable, skip synthesis-only assertions rather than failing the pipeline.
- Do not require cloud services or secret provisioning for the pilot.
- Keep the feature disabled by default in CI unless a dedicated integration job explicitly enables it.

### CI assertions
- import paths resolve
- feature flag off keeps OpenClaw behavior unchanged
- env override map resolves as expected
- any end-to-end WAV generation test emits valid audio artifacts

---

## 6) Rollout notes

### Rollout
1. Merge the additive adapter/shim/tests/docs changes on the feature branch.
2. Run local unit tests first, then the demo smoke test.
3. Validate the generated WAVs.
4. Enable `VOICEDNA_OPENCLAW_PRESETS=1` only for a small pilot group.
5. Expand only after confirming no regressions in default TTS behavior.

### Rollout guardrails
- Keep the feature off unless explicitly enabled.
- Keep the pilot preset set limited to `neutral`, `friendly`, `flair`.
- Keep the integration local-first; do not introduce cloud dependencies.

---

## 7) Rollback notes

1. Unset `VOICEDNA_OPENCLAW_PRESETS` and `VOICEDNA_OPENCLAW_PRESETS_MAP`.
2. Revert any live hook call-site change if one was added.
3. Re-run the existing OpenClaw TTS path to confirm it still works without VoiceDNA.
4. If needed, revert the integration commit(s); no schema or data migration is involved.

---

## 8) Prioritized TODO list for Dr Voss

1. **Wire the narrowest TTS boundary** so `agent_id` is available at the call site and the VoiceDNA bridge can be invoked without touching unrelated paths.
2. **Lock the opt-in gate** so `VOICEDNA_OPENCLAW_PRESETS` is the only enable switch for the pilot.
3. **Verify the fallback chain** (`agent_id` → `agent_name` → default) with tests before any broader rollout.
4. **Run the demo + WAV validation** and archive the artifact paths for review.
5. **Add/confirm CI skips** for synthesis-only tests when the backend is missing.
6. **Sync docs** so the operator-facing runbook matches the final env/config behavior.

---

## 9) Quick acceptance checklist

- [ ] Default VoiceDNA and OpenClaw behavior unchanged when the feature is off
- [ ] Feature flag enables routing only when explicitly set
- [ ] Preset map resolves in the documented order
- [ ] Demo emits three valid WAV files
- [ ] Unit tests pass locally
- [ ] Synthesis tests skip cleanly when backend support is absent
- [ ] Rollback is a config un-set or commit revert, not a migration

---

## 10) Handoff summary

This integration is already structured correctly for a safe pilot: keep the adapter lazy, keep routing opt-in, and only wire the agent-aware TTS boundary. The highest-leverage next step is to confirm the exact OpenClaw call site where `agent_id` is present, then connect it to the VoiceDNA bridge with fallback preserved.
