# Changelog

All notable changes to this project are documented here.

## [2.7.0] - 2026-02-24
### Added
- New `voicedna/consistency.py` with `VoiceConsistencyEngine`, cosine similarity helpers, optional SpeechBrain/Resemblyzer extraction, and deterministic fallback embedding behavior.
- New optional dependency extra `consistency` in `pyproject.toml` for speaker-recognition backends.
- Subtle sonic watermarking pass that embeds `voice_fingerprint_id` markers into WAV output.

### Changed
- `VoiceDNA.create_new()` now upgrades `core_embedding` generation through the consistency engine (audio imprint extraction when available, deterministic fallback otherwise).
- `ImprintConverterFilter` now enforces embedding consistency with threshold `0.92`, applying gentle parametric correction when needed.
- Processor report now includes top-level `consistency_score` and `rvc_ready` fields plus extra consistency metadata under `imprint_converter`.
- Version bumped to `2.7.0`.

### Notes
- v2.7 locks in stronger long-term voice identifiability while preserving natural maturation.

## [2.6.1] - 2026-02-23
### Added
- New maintainer section in README with exact PyPI publish commands using `TWINE_USERNAME` / `TWINE_PASSWORD`.
- Prepared secondary PyPI package badge link beside the existing PyPI version badge.

### Changed
- Version bumped to `2.6.1`.
- Updated `pyproject.toml` license metadata to modern SPDX string format (`license = "MIT"`) to remove setuptools deprecation warnings.
- Omarchy README "Try it now" one-liner clarified and daemon silent-background behavior explicitly documented.

### Notes
- v2.6.1 hardening + PyPI publish instructions.

## [2.6.0] - 2026-02-23
### Added
- Omarchy hardening pass with boot-persistent background daemon support via `voicedna-os-daemon.service`.
- Daemon runtime script for encrypted DNA auto-load on login/reboot with env/keyring fallback support.
- README polish: PyPI badge, clearer quick-start pathing, and one-click Omarchy highlight.

### Changed
- Version bumped to `2.6.0`.
- Omarchy installer now installs daemon artifacts, writes daemon env config, and enables the systemd user service.

### Notes
- Real PyPI publish attempted using `python -m twine upload dist/* --skip-existing`.
- VoiceDNA reaches a new milestone: first OS path where your desktop can grow up with you.

## [2.5.0] - 2026-02-23
### Added
- Full Omarchy (Arch + Hyprland) system-voice integration path under `examples/omarchy/`.
- PipeWire VoiceDNA filter shim (`voicedna-pipewire-filter.py`) for desktop TTS interception + processing.
- Drop-in speech-dispatcher profile (`speech-dispatcher-voicedna.conf`) so Orca/desktop speech can default to VoiceDNA.
- One-command Omarchy installer (`install-voicedna-omarchy.sh`) for setup + service restarts.

### Changed
- Version bumped to `2.5.0`.
- README now includes a dedicated Omarchy system-wide voice section directly after OpenClaw.

### Notes
- PyPI publish validation is fully prepared (`python -m build`, `twine check dist/*`).
- Upload is intentionally manual: `python -m twine upload dist/*`.
- Now your entire desktop can grow up with you.

## [2.4.0] - 2026-02-23
### Added
- New OpenClaw integration testing path under `examples/openclaw/` with a 5-minute setup guide for fresh and existing deployments.
- `examples/openclaw/voicedna_tts_hook.py` skill-ready TTS hook that loads encrypted VoiceDNA (`myai.voicedna.enc`), processes raw audio bytes, and logs full processor reports.
- `examples/openclaw/voipms_phone_skill.py` outbound call example with voip.ms primary flow and Twilio fallback path.

### Changed
- Version bumped to `2.4.0`.
- README now includes a prominent OpenClaw phone testing section directly after demos, including a 3-command quick path.

### Notes
- First real deployment path is now live — you can get phone calls from your growing AI.

## [2.3.0] - 2026-02-23
### Added
- PyPI publish-prep assets: `requirements-dev.txt` and optional `dev` dependency group in `pyproject.toml`.
- RVC-ready stub path in `ImprintConverterFilter` behind `imprint_converter.mode = "rvc_stub"`.
- Processor report fields for imprint converter RVC readiness metadata.

### Changed
- Version bumped to `2.3.0`.
- README updated with top-level PyPI install section and refreshed demo commands.

### Notes
- VoiceDNA now clearly balances cloud services and local Voicebox workflows while preparing for future true RVC conversion integration.

## [2.2.0] - 2026-02-23
### Added
- Cloud demo scripts: `examples/elevenlabs_demo.py` and `examples/cartesia_demo.py`.
- Local/offline Voicebox demo: `examples/voicebox_demo.py` for `http://127.0.0.1:17493/generate`.
- WAV fixture-based test support in `tests/conftest.py`.
- Audio round-trip test in `tests/test_audio_roundtrip.py` proving waveform transformation.

### Changed
- `ImprintConverterFilter` now performs real audio imprint mixing with `pydub` plus WAV fallback path.
- Dependencies updated for v2.2 demos and integrations (`requests` included).
- Package version bumped to `2.2.0`.

### Notes
- VoiceDNA now supports both cloud services and privacy-first local Voicebox flows.

## [2.1.0] - 2026-02-23
### Added
- Real `pydub` audio processing in `AgeMaturationFilter` using frame-rate pitch adjustment.
- Pytest suite in `tests/` with `test_child_inheritance.py` and `test_processor_report.py`.
- Typer CLI in `cli.py` with `voicedna birth`, `voicedna speak`, and `voicedna evolve`.
- Console script entry point (`voicedna`) in `pyproject.toml`.

### Changed
- Package version bumped to `2.1.0`.
- Dependencies updated to include `pydub`, `typer`, and `pytest`.

## [2.0.1] - 2026-02-23
### Added
- `VoiceDNAProcessor.get_last_report()` with per-filter status/duration and chain summary.
- `MIGRATION_v2_0_1.md` with patch upgrade notes.

### Changed
- `VoiceDNA.create_child()` now strictly validates `child_user_name` and `inherit_strength`.
- Processor filter registration now de-duplicates by filter name to avoid double execution.
- CI now performs editable package install (`pip install -e .`) and package import smoke checks.
- Package version bumped to `2.0.1`.

## [2.0.0] - 2026-02-23
### Added
- Real built-in example filters: `AgeMaturationFilter` and `ImprintConverterFilter` in `voicedna/filters/`.
- Child AI inheritance API: `VoiceDNA.create_child(child_user_name, inherit_strength=0.40)`.
- VST3 Python bridge scaffold in `vst3/python_bridge.py` and expanded `vst3/README.md`.
- Open standard draft in `spec/VoiceDNA_Spec_v1.0.md`.
- Announcement templates in `announcements/` for X, OpenClaw issue request, and Reddit.

### Changed
- `VoiceDNAProcessor` now auto-registers built-in filters and keeps robust fail-open chaining with per-filter metrics.
- `pyproject.toml` updated for v2.0 packaging metadata and filter entry points.
- `requirements.txt` now includes `numpy>=2.0.0` for future audio math extension.

## [0.1.8] - 2026-02-23
### Added
- `examples/openclaw_skill.py` one-file integration hook for OpenClaw-style TTS pipelines.
- `vst3/` starter scaffold (`README.md` + `VoiceDNAProcessor.h`) for future JUCE-based binary plugin work.

### Changed
- `voicedna/framework.py` now runs a robust chain with per-filter timing metrics and fail-open behavior when a filter errors.
- `README.md` updated with robust chaining notes, OpenClaw skill usage, and VST3 starter references.

## [0.1.7] - 2026-02-23
### Added
- Encrypted VoiceDNA persistence with `save_encrypted()` and `load_encrypted()` in `voice_dna.py` using `cryptography` (Fernet + PBKDF2-HMAC key derivation).
- `voicedna/framework.py` with `VoiceDNAProcessor` for plugin auto-discovery and chained processing.
- `examples/encrypted_plugin_demo.py` for encrypted load + full processor pipeline demonstration.

### Changed
- `requirements.txt` now includes `cryptography>=43.0.0`.
- `pyproject.toml` now exposes both `voicedna.plugins` and `voicedna.filters` entry-point groups for compatibility.
- `README.md` updated with encrypted framework usage and v1.1 feature overview.

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