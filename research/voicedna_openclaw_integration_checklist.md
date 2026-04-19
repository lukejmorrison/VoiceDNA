# VoiceDNA → OpenClaw per-agent voice integration checklist

## Executive summary
The safe path is already laid out and mostly implemented: VoiceDNA owns the backing `VoiceAdapter` (`voicedna/openclaw_adapter.py`), while OpenClaw owns the opt-in shim (`tools/voicedna_adapter.py`) and runtime gating (`VOICEDNA_OPENCLAW_PRESETS`, `VOICEDNA_OPENCLAW_PRESETS_MAP`). For the next implementation pass, Dr Voss should keep the integration additive, verify the OpenClaw shim + e2e tests, and only touch a live TTS call site if the agent context is actually available there. The conservative default is: do **not** change VoiceDNA core behavior, do **not** change OpenClaw defaults, and keep all per-agent routing behind the env gate.

Validated local artifacts:
- `research/demo_output/demo.wav`
- `examples/openclaw/output/namshub_neutral.wav`
- `examples/openclaw/output/david_friendly.wav`
- `examples/openclaw/output/voss_flair.wav`

---

## Exact entrypoints and functions

### VoiceDNA repo (`/home/namshub/dev/VoiceDNA`)
These are the provider-side contracts and validation hooks:

- `voicedna/openclaw_adapter.py`
  - `load_presets_from_env()` — JSON env parsing for `VOICEDNA_OPENCLAW_PRESETS_MAP`
  - `_build_dna_for_preset()` — preset → synthetic `VoiceDNA`
  - `VoiceAdapter.select_preset(agent_id, agent_name=None)` — deterministic routing
  - `VoiceAdapter.synthesize(text, preset, output_path=None)` — WAV generation + optional file write
  - `VoiceAdapter.register_agent(...)` — runtime mapping helper
- `examples/openclaw_voicedemo.py`
  - `main()` — 3-agent demo, writes WAVs under `examples/openclaw/output/`
- `tests/test_voice_adapter.py`
  - selection logic, env loading, fallback/default, smoke synth paths

### OpenClaw repo (`/home/luke/dev/openclaw`)
These are the consumer-side wiring points already present in the repo:

- `tools/voicedna_adapter.py`
  - `is_voicedna_enabled()` — opt-in gate
  - `_build_preset_map()` — default + env override map
  - `get_voice_adapter()` — singleton adapter factory
  - `reset_adapter()` — test/runtime reset
- `tests/test_voicedna_adapter.py`
  - shim unit tests, no synthesis backend required
- `tests/test_voicedna_e2e.py`
  - end-to-end preset selection + WAV validation
- `demo/voicedna_demo.py`
  - `validate_wav()` and `main()` for demo artifact generation/validation
- `examples/openclaw/voicedna_tts_hook.py`
  - `VoiceDNATTSHook.process_tts_output(...)` — legacy post-TTS hook
  - `wrap_tts_provider(...)` — easiest place to intercept raw TTS bytes if a live wrapper is needed
- `examples/openclaw/voipms_phone_skill.py`
  - `make_growing_voice_call(...)` — downstream call path that already pipes audio through VoiceDNA
- `openclaw.sh`
  - `voice_dna_setup()` / `run_voicedna_cli()` / `voice_dna_registry()` — operational entrypoints for local setup and validation
- Docs to keep synchronized:
  - `DESIGN_DOC_voicedna.md`
  - `VOICEDNA_RUNBOOK.md`
  - `README.md`
  - `skills/voicedna-agent-voices/SKILL.md`

---

## Step-by-step integration checklist

### 1) Confirm the source-of-truth branch and current repo state
Use the exact branch already documented for VoiceDNA and verify the local OpenClaw repo is the intended consumer.

```bash
cd /home/namshub/dev/VoiceDNA
git status --short
git branch --show-current
git describe --tags --always

cd /home/luke/dev/openclaw
git status --short
git branch --show-current
```

Expected:
- VoiceDNA branch should be the per-agent pilot branch or `main` after merge.
- OpenClaw should remain unchanged unless you are updating docs/tests.

---

### 2) Validate the provider-side VoiceDNA contract locally
Run the VoiceDNA adapter tests first. This confirms the preset registry, selection order, and synthesis paths before touching any OpenClaw wiring.

```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -v
ruff check voicedna/openclaw_adapter.py tests/test_voice_adapter.py examples/openclaw_voicedemo.py
```

Acceptance:
- All adapter tests pass.
- Ruff passes on the adapter, tests, and demo.

---

### 3) Validate the OpenClaw shim and e2e contract
These tests prove the OpenClaw side can import the VoiceDNA adapter, build the default preset map, and write valid WAVs when the backend is available.

```bash
cd /home/luke/dev/openclaw
python -m pytest tests/test_voicedna_adapter.py -v
python -m pytest tests/test_voicedna_e2e.py -v
```

If the VoiceDNA repo is absent in the test environment, expect the synthesis cases in `test_voicedna_e2e.py` to skip; that is acceptable as long as the shim tests pass.

---

### 4) Generate and validate demo WAVs locally
Use the VoiceDNA demo script for the provider-side output and the OpenClaw demo script for consumer-side validation. Keep both local-first.

```bash
cd /home/namshub/dev/VoiceDNA
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
file examples/openclaw/output/*.wav
python - <<'PY'
from pathlib import Path
import wave
root = Path('examples/openclaw/output')
for p in sorted(root.glob('*.wav')):
    with wave.open(str(p), 'rb') as w:
        print(p.name, w.getnchannels(), w.getframerate(), w.getsampwidth(), w.getnframes())
PY
```

Validated outputs:
- `examples/openclaw/output/namshub_neutral.wav`
- `examples/openclaw/output/david_friendly.wav`
- `examples/openclaw/output/voss_flair.wav`

Optional smoke artifact:
- `research/demo_output/demo.wav`

Acceptance:
- Three WAVs exist.
- Files are non-empty.
- Headers validate as RIFF PCM 16-bit mono 22050 Hz.

---

### 5) Keep per-agent routing opt-in only
Do not change default OpenClaw behavior. The only activation path should remain the env gate.

Required env vars:

```bash
export VOICEDNA_OPENCLAW_PRESETS=1
export VOICEDNA_OPENCLAW_PRESETS_MAP='{"agent:namshub":"neutral","agent:david-hardman":"friendly","agent:dr-voss-thorne":"flair"}'
```

Optional local VoiceDNA backend controls already supported by the repo:

```bash
export VOICEDNA_PASSWORD='...'
export VOICEDNA_ENC_PATH='...'
export VOICEDNA_FORCE_AGE='15'
```

---

### 6) If live pipeline wiring is needed, touch only the narrowest call site
If the current OpenClaw voice path needs actual runtime routing, prefer a wrapper where `agent_id` is already known. The safest pattern is:

```python
adapter = get_voice_adapter()
if adapter:
    preset = adapter.select_preset(agent_id, agent_name=agent_name)
    wav_bytes = adapter.synthesize(text, preset, output_path=path)
```

Best candidate hook points in OpenClaw:
- `examples/openclaw/voicedna_tts_hook.py:process_tts_output(...)`
- `examples/openclaw/voicedna_tts_hook.py:wrap_tts_provider(...)`
- any agent-specific reply function that already knows the speaker identity

Do **not** thread this into unrelated core paths unless the agent identity is already present.

---

### 7) Record the exact files to change if more wiring is approved
If implementation proceeds beyond the existing shim/demo, the file list should stay small.

#### VoiceDNA repo
- `voicedna/openclaw_adapter.py`
- `examples/openclaw_voicedemo.py`
- `tests/test_voice_adapter.py`
- `README.md` (only if the usage section needs synchronization)

#### OpenClaw repo
- `tools/voicedna_adapter.py`
- `tests/test_voicedna_adapter.py`
- `tests/test_voicedna_e2e.py`
- `demo/voicedna_demo.py`
- `examples/openclaw/voicedna_tts_hook.py` only if the live reply path needs the agent-aware call
- `examples/openclaw/voipms_phone_skill.py` only if call audio should use the new routing path directly
- `.github/workflows/ci.yml` only if CI should run the new shim/e2e tests explicitly
- `README.md`, `VOICEDNA_RUNBOOK.md`, `DESIGN_DOC_voicedna.md`, `skills/voicedna-agent-voices/SKILL.md` for docs sync

---

### 8) Add or confirm packaging/install steps
No new runtime dependency should be needed for the opt-in shim if OpenClaw can import the VoiceDNA repo from disk.

Recommended local install commands:

```bash
cd /home/namshub/dev/VoiceDNA
pip install -e .
# or, for a clean validation env:
pip install -e ".[dev,consistency]"

cd /home/luke/dev/openclaw
python -m pip install -e .
```

Relevant dependency versions currently declared in VoiceDNA `pyproject.toml`:
- `cryptography>=43.0.0`
- `numpy>=2.0.0`
- `pydub>=0.25.1`
- `sounddevice>=0.4.7`
- `typer>=0.12.3`
- `requests>=2.32.0`
- optional `speechbrain>=1.0.0`
- optional `resemblyzer>=0.1.4`
- optional `pytest>=8.2.0`

Conservative rule: do not add new deps unless a missing import is unavoidable.

---

### 9) Update CI only if the runner can actually access the VoiceDNA repo
If you want OpenClaw CI to validate the new integration, add explicit test steps in `.github/workflows/ci.yml` for:

```bash
python -m pytest tests/test_voicedna_adapter.py -v
python -m pytest tests/test_voicedna_e2e.py -v
```

But only do this if the runner can import VoiceDNA from a checked-out path or an installed wheel. Otherwise keep these as local/manual verification and avoid flaky CI.

Recommended conservative CI stance:
- Keep the existing OpenClaw CI green.
- Add shim/e2e tests only if the VoiceDNA backend is made available in CI by design.

---

### 10) Stage reviewer-ready artifacts and handoff notes
If the integration is meant for review, stage the outputs in the shared artifacts path and record test results.

```bash
mkdir -p /home/namshub/.openclaw/workspaces/namshub/artifacts/voicedna-demo
cp /home/namshub/dev/VoiceDNA/examples/openclaw/output/*.wav \
  /home/namshub/.openclaw/workspaces/namshub/artifacts/voicedna-demo/

cp /home/namshub/dev/VoiceDNA/research/voicedna_openclaw_integration_checklist.md \
  /home/namshub/.openclaw/workspaces/namshub/handoffs/voicedna_handoff.md
```

If the repo uses a PR draft or bundle handoff, keep the bundle path documented and avoid pushing without approval.

---

## `prep.sh` snippet
Copy/pasteable local prep script:

```bash
#!/usr/bin/env bash
set -euo pipefail

VOICE_DNA_REPO=/home/namshub/dev/VoiceDNA
OPENCLAW_REPO=/home/luke/dev/openclaw
ARTIFACTS=/home/namshub/.openclaw/workspaces/namshub/artifacts/voicedna-demo

cd "$VOICE_DNA_REPO"
python -m pytest tests/test_voice_adapter.py -v
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
file examples/openclaw/output/*.wav

python - <<'PY'
from pathlib import Path
import struct
for p in sorted(Path('examples/openclaw/output').glob('*.wav')):
    data = p.read_bytes()
    assert data[:4] == b'RIFF' and data[8:12] == b'WAVE'
    audio_format, channels, sample_rate, _, _, bits = struct.unpack_from('<HHIIHH', data, 20)
    assert (audio_format, channels, sample_rate, bits) == (1, 1, 22050, 16)
    print('validated', p.name, len(data))
PY

mkdir -p "$ARTIFACTS"
cp examples/openclaw/output/*.wav "$ARTIFACTS"/

cd "$OPENCLAW_REPO"
python -m pytest tests/test_voicedna_adapter.py -v
python -m pytest tests/test_voicedna_e2e.py -v
```

---

## Example diff snippets for the live wrapper path

If Dr Voss decides to wire the agent-aware preset selection into a live reply wrapper, the diff should be tiny and local:

```diff
- raw_bytes = tts_provider.render(text)
- return postprocess(raw_bytes)
+ adapter = get_voice_adapter()
+ if adapter:
+     preset = adapter.select_preset(agent_id, agent_name=agent_name)
+     return adapter.synthesize(text, preset, output_path=output_path)
+ raw_bytes = tts_provider.render(text)
+ return postprocess(raw_bytes)
```

For the OpenClaw shim, the important guard stays the same:

```diff
- if not enabled:
-     return None
+ if not enabled:
+     return None  # preserve default behavior
```

---

## CI / release / PR checklist

### CI
- [ ] Keep existing OpenClaw CI passing.
- [ ] Add `tests/test_voicedna_adapter.py` and `tests/test_voicedna_e2e.py` only if the runner can import VoiceDNA reliably.
- [ ] Do not make the workflow depend on secrets unless absolutely necessary.

### Release / packaging
- [ ] Use `pip install -e /home/namshub/dev/VoiceDNA` for local verification.
- [ ] If a packaged artifact is required, build it explicitly and document the exact wheel/bundle command.
- [ ] Keep `VoiceDNA` version metadata and released tag notes consistent before publishing.

### PR checklist
- [ ] Link the PR to `DESIGN_DOC_voicedna.md` or the VoiceDNA integration doc.
- [ ] Mention the env gate and rollback (`unset VOICEDNA_OPENCLAW_PRESETS`, `unset VOICEDNA_OPENCLAW_PRESETS_MAP`).
- [ ] Include test output summary and demo WAV validation.
- [ ] Include artifact locations for reviewer copies.
- [ ] State clearly that default behavior is unchanged.

### Suggested `PR_BODY.md` snippet

```md
## Summary
Wire VoiceDNA per-agent voice routing into OpenClaw behind an opt-in env gate.

## What changed
- Added/verified VoiceDNA `VoiceAdapter` contract and demo WAV generation.
- Kept OpenClaw shim opt-in via `VOICEDNA_OPENCLAW_PRESETS`.
- Added tests for preset selection, env loading, and WAV validation.

## Validation
- `python -m pytest tests/test_voice_adapter.py -v`
- `python -m pytest tests/test_voicedna_adapter.py -v`
- `python -m pytest tests/test_voicedna_e2e.py -v`
- `VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py`

## Rollback
Unset `VOICEDNA_OPENCLAW_PRESETS` and `VOICEDNA_OPENCLAW_PRESETS_MAP`.
```

---

## Blockers / human approvals

1. **GitHub PAT needed for any push or PR creation**
   - Mitigation: keep everything local, prepare a bundle/draft PR body, and hand off exact commands only.

2. **CI secrets or hosted backend access** if the integration is expected to run synthesis in GitHub Actions
   - Mitigation: keep e2e synthesis local-only or mark it skip-safe when the VoiceDNA backend is absent.

3. **Runtime access to the live OpenClaw host** if Dr Voss needs to wire a real agent voice call path
   - Mitigation: validate with the shim/demo first, then apply the narrowest wrapper change on the target host.

4. **Voice/data licensing review if future presets are not the built-in pilot trio**
   - Current pilot status: no blocker found for `neutral`, `friendly`, `flair`.
   - Mitigation: keep any third-party sample packs or proprietary voices out of the repo until redistribution rights are explicitly approved.

5. **Version metadata mismatch risk** (`pyproject.toml` currently shows `3.0.0`, while release notes mention `v3.1.1`)
   - Mitigation: use editable local installs and keep the branch/tag/release note consistent before publishing.

---

## One-paragraph blocker + next-step summary
The integration is best treated as an opt-in consumer-side shim with a provider-side contract already in place, so the safest next step is to validate the existing `VoiceAdapter`/shim/demo/test path end-to-end and only wire a live OpenClaw TTS wrapper if the agent identity is already available at that call site. The main blockers are procedural rather than technical: a GitHub PAT for any push/PR, possible CI secret/runtime limitations if synthesis is moved into CI, and the need to keep the VoiceDNA version metadata aligned with the released tag. Immediate next step: run the two test suites, generate and validate the three demo WAVs, then hand Dr Voss the exact live wrapper file to patch if a runtime hook is still required.
