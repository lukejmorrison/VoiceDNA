# PR CHECKLIST — VoiceDNA per-agent voice pilot

Branch: `feature/voicedna-openclaw-per-agent-voices`
Run label: `voiceDNA-research-prep`

## Required reviewers
- Namshub
- Dr Voss Thorne
- Optional: Luke for product/UX sanity on the OpenClaw persona mapping

## Acceptance criteria
- [x] Three presets exist: `neutral`, `friendly`, `flair`
- [x] Preset selection is deterministic: `agent_id` -> `agent_name` -> default
- [x] The demo maps the three OpenClaw personas to three distinct presets
- [x] The adapter is opt-in and does not change default VoiceDNA behavior
- [x] Targeted tests pass locally
- [x] Demo output files exist and are non-empty in the repo
- [ ] Full repo test suite passes in a dependency-complete environment

## QA steps
- [x] Run `python -m pytest tests/test_voice_adapter.py -v`
- [ ] Run `python -m pytest -q` in a venv with all project dependencies installed
- [ ] Run `python examples/openclaw_voicedemo.py` in an environment that includes the VoiceDNA runtime backend stack
- [x] Verify demo WAVs exist under `examples/openclaw/output/`
- [x] Verify `ruff check voicedna/openclaw_adapter.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py`
- [ ] Verify any repo-wide type/lint jobs configured for the project

## Test matrix
| Area | Command | Status |
|---|---|---|
| Voice adapter unit tests | `python -m pytest tests/test_voice_adapter.py -v` | PASS (15 passed, 3 skipped) |
| Repo pytest | `python -m pytest -q` | BLOCKED by missing `cryptography` |
| Ruff | `ruff check voicedna/openclaw_adapter.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py` | PASS |
| Demo script | `python examples/openclaw_voicedemo.py` | BLOCKED by missing runtime backend packages |
| Syntax compile | `python -m py_compile voicedna/openclaw_adapter.py examples/openclaw_voicedemo.py tests/test_voice_adapter.py` | PASS |

## Files changed and rationale
- `voicedna/openclaw_adapter.py` — per-agent routing layer and pilot preset registry
- `examples/openclaw_voicedemo.py` — local reproducible demo
- `tests/test_voice_adapter.py` — focused smoke/unit coverage
- `README.md` / `CHANGELOG.md` / `IMPLEMENTATION_NOTE.md` — docs and run guidance
- `research/summary_for_pr.md` — concise executive summary for the PR
- `examples/openclaw/output/*.wav` — sample outputs for review

## Reference cross-check
- Design doc summary: `research/summary_for_pr.md`
- Detailed implementation note: `IMPLEMENTATION_NOTE.md`
- Validation log: `research/RESEARCH_VALIDATION.txt`
- Test matrix: `research/TEST_SUMMARY.txt`
- Git workflow rules: `SKILL_GIT_WORKFLOW.md`
- CI workflow: `.github/workflows/ci.yml`
- Issue automation workflows: `.github/workflows/feedback-helper.yml`, `.github/workflows/auto-label-feedback.yml`

## Merge steps
1. Re-run the repo-wide test suite in a clean dependency environment.
2. Re-run the demo when the runtime backend is available.
3. Confirm no unintended files are included in the PR.
4. Merge after reviewer sign-off and QA confirmation.

## GitHub workflow permission note
- This branch does **not** change any `.github/workflows/*` files relative to `origin/main`.
- Therefore no workflow-permission push blocker is expected from this branch as-is.
- If a future update adds or modifies workflow files, GitHub may reject the push with a message similar to:
  - `remote: error: GH006: Protected branch update failed for refs/heads/...`
  - or workflow-specific restrictions on `.github/workflows/*` changes depending on repo policy.

## Current readiness
- Ready for PR review: yes, with the noted environment blockers documented.
