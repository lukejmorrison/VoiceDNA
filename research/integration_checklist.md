# VoiceDNA → OpenClaw integration checklist

**Branch:** `feat/voicedna-openclaw-integration`
**Release anchor:** VoiceDNA `v3.1.1` (`69d8d0c`)

Use this as a go/no-go checklist before wiring the live OpenClaw TTS seam.

## Legend
- **PASS** — the criterion is satisfied now
- **FAIL** — the criterion is not satisfied and needs work
- **BLOCKED** — cannot be completed in the current environment
- **N/A** — not applicable for this rollout

| Step | Command / action | Pass criterion | Current evidence | Status |
|---|---|---|---|---|
| 1 | `cd /home/namshub/dev/VoiceDNA && git describe --tags --exact-match 69d8d0c` | Prints `v3.1.1` | Verified in prior research packet | PASS |
| 2 | `python -m pytest tests/test_voice_adapter.py -v` | Exit code 0; adapter tests pass | Prior run: `15 passed, 3 skipped` | PASS |
| 3 | `python -m pytest tests/test_openclaw_live_voice.py -v` | Exit code 0; live integration tests pass | Prior run: `12 passed` | PASS |
| 4 | `python -m pytest -q` | Whole VoiceDNA suite passes in a dependency-complete venv | Prior run: `46 passed in 1.86s` | PASS |
| 5 | `ruff check voicedna/openclaw_adapter.py voicedna/openclaw_live_voice.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py tests/test_openclaw_live_voice.py` | Exit code 0 | Prior run clean | PASS |
| 6 | `python -m py_compile voicedna/openclaw_adapter.py voicedna/openclaw_live_voice.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py tests/test_openclaw_live_voice.py` | No syntax errors | Prior run clean | PASS |
| 7 | `VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py` | Creates 3 WAVs under `examples/openclaw/output/` | Prior run wrote `164696`, `211876`, `209542` byte files | PASS |
| 8 | `stat -c '%n %s bytes' examples/openclaw/output/*.wav` | All 3 files are non-empty | Prior run confirmed all files non-empty | PASS |
| 9 | `cd /home/namshub/dev/openclaw && python -m pytest tests/test_voicedna_adapter.py -v` | OpenClaw shim tests pass | Prior run documented separately in OpenClaw repo | PASS |
| 10 | Verify `VOICEDNA_OPENCLAW_PRESETS=1` and `VOICEDNA_OPENCLAW_PRESETS_MAP=...` are set in the active OpenClaw env file | Feature flag and map are present exactly once | Must be confirmed in target runtime | BLOCKED until rollout env is updated |
| 11 | Verify the live seam only routes through VoiceDNA when the flag is enabled | Existing TTS remains fallback when flag is absent | Design requirement; already reflected in docs/tests | PASS |
| 12 | Confirm no `.github/workflows/*` files changed | No workflow permission uplift needed | Prior CI/permissions review shows no workflow diff | PASS |
| 13 | Confirm rollback by unsetting both env vars and restarting the service | Default behavior is restored | Not yet exercised in target runtime | N/A |

## Acceptance criteria

A rollout is ready when all of the following are true:

- [x] VoiceDNA `v3.1.1` tag resolves locally
- [x] Adapter tests pass
- [x] Live integration tests pass
- [x] Repo-wide VoiceDNA test suite passes in a clean dependency environment
- [x] Demo outputs are generated and non-empty
- [ ] Active OpenClaw runtime has the feature flag + preset map set in its env file
- [ ] OpenClaw service has been restarted and smoke-tested with the new env
- [ ] No unintended files are staged for the PR

## Manual pass/fail checks

### A. Preset routing
- **PASS** when:
  - `agent:namshub` → `neutral`
  - `agent:david-hardman` → `friendly`
  - `agent:dr-voss-thorne` → `flair`
- **FAIL** when any agent resolves to the wrong preset.

### B. Fallback behavior
- **PASS** when disabling `VOICEDNA_OPENCLAW_PRESETS` restores the original OpenClaw TTS path without errors.
- **FAIL** when the flag is required just to boot or when TTS breaks with the flag off.

### C. Output artifacts
- **PASS** when these files exist and are non-empty:
  - `examples/openclaw/output/namshub_neutral.wav`
  - `examples/openclaw/output/david_friendly.wav`
  - `examples/openclaw/output/voss_flair.wav`
- **FAIL** when any file is missing, empty, or malformed.

### D. Permissions
- **PASS** when the PR can be pushed and opened with only `contents:write` + `pull_requests:write`.
- **FAIL** only if a future change touches `.github/workflows/*` and needs `workflow` scope.

## Rollback checklist

- [ ] Unset `VOICEDNA_OPENCLAW_PRESETS`
- [ ] Unset `VOICEDNA_OPENCLAW_PRESETS_MAP`
- [ ] Restart the OpenClaw service
- [ ] Confirm the old TTS path is back
- [ ] Revert the seam hook if the PR must be backed out

## Notes

- No migrations are required.
- No deploy key or service-account secret is required for the preset pilot.
- If the team later switches to encrypted `.voicedna.enc` routing, capture the needed `VOICEDNA_PASSWORD_*` values from the team secret store rather than pasting them into chat.