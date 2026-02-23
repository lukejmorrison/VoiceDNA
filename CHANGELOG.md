# Changelog

All notable changes to this project are documented here.

## [0.1.6] - 2026-02-23
### Added
- GitHub Action workflow (`.github/workflows/auto-label-feedback.yml`) that auto-adds the `feedback` label when issue title/body contains feedback-oriented keywords.
- Keyword-based labeling trigger (`feedback`, `suggestion`, `improvement`, `enhancement`, `idea`, `request`, `proposal`, `roadmap`, `polish`) to accelerate the feedback loop.

## [0.1.5] - 2026-02-23
### Added
- GitHub Action workflow (`.github/workflows/feedback-helper.yml`) that auto-comments a ready `scripts/review_feedback.py` command on issues labeled `feedback`.
- Duplicate-comment guard via hidden marker to avoid repeated helper comments on the same issue.

## [0.1.4] - 2026-02-23
### Added
- `scripts/review_feedback.py` to append structured feedback updates into `EVOLUTION.md`.
- README documentation for running the feedback logger with repeatable `--actions` and `--next` fields.

## [0.1.3] - 2026-02-23
### Added
- Entry-point plugin auto-discovery in `PluginManager` via `load_entrypoint_plugins()`.
- Packaging metadata in `pyproject.toml` with `voicedna.plugins` entry-point group.
- External plugin registration docs in `README.md`.
- `CHANGELOG.md` and `EVOLUTION.md` for transparent project evolution.

### Changed
- `examples/openclaw_hook.py` now attempts entry-point discovery first and falls back to built-in filters.

## [0.1.2] - 2026-02-23
### Added
- `.gitignore` with Python and generated artifact ignores.
- `examples/demo.py` with create/load/evolve prompt flow.

### Changed
- Unified UTC timestamp generation style in `voice_dna.py`.
- CI workflow expanded to cover new examples.

## [0.1.1] - 2026-02-23
### Added
- `voicedna` package scaffold with plugin API and manager.
- Built-in filters and OpenClaw-style hook example.
- CI compile/smoke checks for plugin files.

## [0.1.0] - 2026-02-23
### Added
- Initial VoiceDNA core (`voice_dna.py`).
- README, MIT license, schema, examples, and baseline CI.