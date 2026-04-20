# VoiceDNA → OpenClaw live per-agent voice integration plan

**Branch for implementation:** `feature/voicedna-openclaw-live-seam`

**Goal:** wire `voicedna.openclaw_adapter.VoiceAdapter` into the live OpenClaw agent voice path in a way that stays additive, opt-in, and easy to roll back.

**What is already true in the workspace**
- VoiceDNA has the pilot adapter and demo:
  - `voicedna/openclaw_adapter.py`
  - `examples/openclaw_voicedemo.py`
  - `tests/test_voice_adapter.py`
  - `tests/test_openclaw_live_voice.py`
- OpenClaw already has an opt-in shim and shim tests:
  - `tools/voicedna_adapter.py`
  - `tools/voicedna_tts_hook.py`
  - `tests/test_voicedna_adapter.py`
  - `tests/test_voicedna_e2e.py`
- OpenClaw also has the live TTS shell seam that can stay unchanged unless the agent identity is passed there:
  - `skills/audio-responder-tts/audio_tts_reply.sh`
  - `skills/audio-responder-tts/SKILL.md`

**Important note:** some docs still mention `voicedna/openclaw_live_voice.py` and `examples/openclaw/voicedna_tts_hook.py`. Those paths are not present in the current VoiceDNA tree / OpenClaw tree as source files. Treat them as stale references unless Dr Voss intentionally restores them.

---

## Exact file targets

### VoiceDNA repo (`/home/namshub/dev/VoiceDNA`)
These are the provider-side files to keep in sync if any final polish is needed:
- `voicedna/openclaw_adapter.py`
- `examples/openclaw_voicedemo.py`
- `tests/test_voice_adapter.py`
- `tests/test_openclaw_live_voice.py`
- `README.md` (usage note sync only)
- `pyproject.toml` (only if packaging/import behavior changes)

### OpenClaw repo (`/home/namshub/dev/openclaw`)
These are the consumer-side live wiring files:
- `tools/voicedna_adapter.py` — opt-in gate + preset map source of truth
- `tools/voicedna_tts_hook.py` — canonical runtime seam for `render_agent_voice(...)`
- `tests/test_voicedna_adapter.py` — shim behavior, env parsing, singleton reset
- `tests/test_voicedna_e2e.py` — preset routing + WAV smoke coverage
- `skills/audio-responder-tts/audio_tts_reply.sh` — only if the shell path needs agent identity passed through
- `skills/audio-responder-tts/SKILL.md` — only after runtime seam is proven
- `README.md`, `VOICEDNA_RUNBOOK.md`, `DESIGN_DOC_voicedna.md` — docs sync only

---

## Integration shape

### Recommended rule
Keep **one** canonical runtime seam in OpenClaw:
- Preferred: `tools/voicedna_tts_hook.py:render_agent_voice(text, agent_id, agent_name=None, output_path=None)`
- Optional shell wrapper only if the current live reply path starts in `audio_tts_reply.sh`

### Selection order
Use the VoiceDNA adapter’s deterministic routing order:
1. `agent_id`
2. `agent_name`
3. default preset

### Presets
Use only the pilot presets already shipped:
- `neutral`
- `friendly`
- `flair`

### Opt-in gate
Default behavior must remain unchanged unless the user explicitly enables VoiceDNA routing:
- `VOICEDNA_OPENCLAW_PRESETS=1`
- optional override map: `VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'`

---

## Step-by-step implementation plan

### 1) Keep the shim boundary explicit
Confirm the OpenClaw shim remains the only activation path.
- `tools/voicedna_adapter.py:get_voice_adapter()` should return `None` when the flag is unset.
- The default TTS path must remain the fallback.
- Do not change public OpenClaw CLI/skill behavior for users who never set the env var.

**Smoke check**
```bash
cd /home/namshub/dev/openclaw
python -m pytest tests/test_voicedna_adapter.py -v
```
**Expected:** `14 passed` with no failures.

---

### 2) Route the live voice seam only where agent identity is already known
Patch the narrowest OpenClaw call site that already knows `agent_id` and optionally `agent_name`.
- Prefer `tools/voicedna_tts_hook.py` over a broad core refactor.
- If the current live path reaches `audio_tts_reply.sh`, pass the agent identity through without changing output formats.
- Keep the fallback call path intact when `get_voice_adapter()` returns `None`.

**Suggested code shape**
```python
adapter = get_voice_adapter()
if adapter is None:
    return fallback_tts(text, output_path=output_path)

preset = adapter.select_preset(agent_id, agent_name=agent_name)
return adapter.synthesize(text, preset, output_path=output_path)
```

---

### 3) Keep the preset map as the source of truth
Use the built-in pilot defaults unless the env map overrides them.
- `agent:namshub` → `neutral`
- `agent:david-hardman` → `friendly`
- `agent:dr-voss-thorne` → `flair`

If `VOICEDNA_OPENCLAW_PRESETS_MAP` is malformed JSON, fail closed and fall back to the built-in defaults.

**Smoke check**
```bash
cd /home/namshub/dev/openclaw
python -m pytest tests/test_voicedna_e2e.py -v
```
**Expected:** `18 passed` or `skipped` for backend-dependent cases if VoiceDNA cannot synthesize locally.

---

### 4) Keep VoiceDNA packaging conservative
No new runtime dependency should be introduced unless the live seam truly needs one.
- Prefer using the installed `voicedna` package from the VoiceDNA checkout.
- Avoid hardcoding workspace-only import paths in a shipping path.
- If the OpenClaw repo must import VoiceDNA in production, make that dependency explicit in packaging or deploy docs instead of relying on a local absolute path.

**Potential packaging/dependency issue to resolve before shipping:**
- `tools/voicedna_adapter.py` currently relies on `/home/namshub/dev/VoiceDNA` being present on disk.
- That is acceptable for local development, but it is not a shipping-grade dependency contract.
- Fix by requiring an installed `voicedna` wheel or a configurable import path.

---

### 5) Update docs only after the seam works
Once the seam is stable, synchronize the docs:
- `skills/audio-responder-tts/SKILL.md`
- `VOICEDNA_RUNBOOK.md`
- `README.md`
- `DESIGN_DOC_voicedna.md`

Keep the docs short and opt-in focused. Mention:
- env gate
- default fallback behavior
- the three pilot presets
- rollback by unsetting the env vars

---

## Smoke-test matrix

### VoiceDNA repo
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -q
python -m pytest tests/test_openclaw_live_voice.py -q
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
python -m py_compile voicedna/openclaw_adapter.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py tests/test_openclaw_live_voice.py
```

**Expected outputs**
- `tests/test_voice_adapter.py`: `18 passed`
- `tests/test_openclaw_live_voice.py`: `13 passed`
- demo writes:
  - `examples/openclaw/output/namshub_neutral.wav`
  - `examples/openclaw/output/david_friendly.wav`
  - `examples/openclaw/output/voss_flair.wav`
- demo WAVs should be non-empty RIFF PCM 16-bit mono 22050 Hz files

### OpenClaw repo
```bash
cd /home/namshub/dev/openclaw
python -m pytest tests/test_voicedna_adapter.py -v
python -m pytest tests/test_voicedna_e2e.py -v
python -m py_compile tools/voicedna_adapter.py tools/voicedna_tts_hook.py tests/test_voicedna_adapter.py tests/test_voicedna_e2e.py
```

**Expected outputs**
- `tests/test_voicedna_adapter.py`: `14 passed`
- `tests/test_voicedna_e2e.py`: `18 passed` or backend-dependent skips if synthesis is unavailable

---

## Missing files / gaps to flag before shipping

1. **`voicedna/openclaw_live_voice.py` is referenced in docs, but not present in the current VoiceDNA tree.**
   - If that module is still intended to exist, it needs to be added back.
   - If not intended, remove stale references from docs/tests to avoid confusion.

2. **`examples/openclaw/voicedna_tts_hook.py` is referenced by some docs, but the current OpenClaw live seam is `tools/voicedna_tts_hook.py`.**
   - Keep one canonical seam; do not maintain two divergent hook implementations.

3. **The current OpenClaw shim uses a workspace absolute path.**
   - This must be resolved for shipping: packaged dependency, editable install, or configurable import root.

4. **Generated audio artifacts should not be treated as source assets.**
   - If any WAV examples are committed, confirm they are intentionally distributable and not tied to third-party license constraints.

---

## Licensing / asset check

- VoiceDNA is MIT licensed, so the code itself is not blocked by a copyleft issue.
- I did **not** find a bundled third-party voice asset that obviously blocks shipping.
- Main caution: any demo WAVs or preset assets should be treated as generated artifacts unless provenance and redistribution rights are documented.
- If future preset voices depend on external sample libraries or proprietary voice models, capture license terms before bundling.

---

## Ticket-sized tasks for Dr Voss

### Ticket 1 — Wire the live seam through the canonical OpenClaw hook
**Branch:** `feature/voicedna-openclaw-live-seam`
**Files:**
- `tools/voicedna_tts_hook.py`
- `tools/voicedna_adapter.py` if the seam needs stricter env gating
**Goal:** route text through `VoiceAdapter` when `VOICEDNA_OPENCLAW_PRESETS=1`, otherwise preserve current TTS behavior.
**Minimal repro:**
```bash
cd /home/namshub/dev/openclaw
VOICEDNA_OPENCLAW_PRESETS=1 python -m pytest tests/test_voicedna_tts_hook.py -v
```

### Ticket 2 — Pass agent identity into the live voice seam
**Branch:** `feature/voicedna-openclaw-live-seam`
**Files:**
- `skills/audio-responder-tts/audio_tts_reply.sh`
- `tools/voicedna_tts_hook.py`
**Goal:** ensure the seam receives `agent_id` and optional `agent_name` without changing output formats.
**Minimal repro:**
```bash
cd /home/namshub/dev/openclaw
python -m pytest tests/test_voicedna_tts_hook.py -v
```

### Ticket 3 — Harden the shim and preset-map contract
**Branch:** `feature/voicedna-openclaw-live-seam`
**Files:**
- `tests/test_voicedna_adapter.py`
- `tests/test_voicedna_e2e.py`
- `tools/voicedna_adapter.py`
**Goal:** confirm opt-in gating, JSON map parsing, fallback behavior, and singleton reset.
**Minimal repro:**
```bash
cd /home/namshub/dev/openclaw
python -m pytest tests/test_voicedna_adapter.py tests/test_voicedna_e2e.py -v
```

### Ticket 4 — Clean up docs and remove stale path references
**Branch:** `feature/voicedna-openclaw-live-seam`
**Files:**
- `README.md`
- `VOICEDNA_RUNBOOK.md`
- `DESIGN_DOC_voicedna.md`
- `skills/voicedna-agent-voices/SKILL.md`
**Goal:** document one canonical hook path, the env gate, rollback, and the three pilot presets.
**Minimal repro:**
```bash
rg -n "voicedna_live_voice|voicedna_tts_hook|VOICEDNA_OPENCLAW_PRESETS" README.md VOICEDNA_RUNBOOK.md DESIGN_DOC_voicedna.md skills/voicedna-agent-voices/SKILL.md
```

### Ticket 5 — Packaging decision: remove workspace-only import reliance
**Branch:** `feature/voicedna-openclaw-live-seam`
**Files:**
- `tools/voicedna_adapter.py`
- `pyproject.toml` or deploy docs, depending on chosen packaging path
**Goal:** make VoiceDNA import resolution ship-safe instead of depending on `/home/namshub/dev/VoiceDNA`.
**Minimal repro:**
```bash
cd /home/namshub/dev/openclaw
python -m pytest tests/test_voicedna_adapter.py -v
```

---

## Short implementation order
1. Patch `tools/voicedna_tts_hook.py` to accept agent identity and call `VoiceAdapter`.
2. Propagate agent identity from the live shell path if needed.
3. Harden tests and ensure all shim/e2e tests pass.
4. Update docs once the runtime seam is proven.
5. Decide whether to package VoiceDNA as a dependency or keep the path local-only.

---

## Rollback plan
- Unset `VOICEDNA_OPENCLAW_PRESETS`.
- Unset `VOICEDNA_OPENCLAW_PRESETS_MAP`.
- Revert only the narrow seam patch if live routing needs to be disabled.
- Existing OpenClaw TTS behavior should remain intact for everyone else.
