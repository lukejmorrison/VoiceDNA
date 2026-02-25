# Changelog

All notable changes to this project are documented here.

## [2.9.8] - 2026-02-25
### Added
- Added new `voicedna doctor-natural` command with quick VRAM/runtime health checks and optional immediate natural test run.
- Added lightweight backend preflight checks for PersonaPlex and Piper to provide clear readiness diagnostics before synthesis.

### Changed
- Improved `voicedna test-natural` output with explicit natural test summary, final backend, recommendations, and Piper model visibility.
- Improved Piper fallback quality by adding auto model discovery and tuned default prosody knobs (`length_scale`, `noise_scale`, `noise_w`).
- Updated Omarchy daemon/test docs to recommend `doctor-natural` as the first natural voice validation path.
- Version bumped to `2.9.8`.

### Notes
- v2.9.8 is tuned for smoother, clearer natural voice testing on 8GB GPUs (for example GTX 1070 Ti).

## [2.9.7] - 2026-02-25
### Added
- Added `SKILL_GIT_WORKFLOW.md` documenting Peter-style parallel checkout workflow for multi-agent isolation.

### Changed
- Added top-level README agent workflow note pointing to `SKILL_GIT_WORKFLOW.md`.
- Version bumped to `2.9.7`.

### Notes
- Adopted parallel checkouts (`voiceDNA-codex`, `voiceDNA-grok`) so Codex and Grok can work safely without interfering.

## [2.9.6] - 2026-02-24
### Added
- Added new optional dependency extra `personaplex-lowvram` with `bitsandbytes` and PersonaPlex runtime stack for 4-bit loading.
- Added `--lowvram` flag to `voicedna speak` and `voicedna test-natural` to force 4-bit PersonaPlex mode with offload safety.
- Added Omarchy installer support for `--lowvram` and daemon env knobs for low-VRAM PersonaPlex operation.

### Changed
- PersonaPlex provider now auto-detects VRAM and loads 4-bit quantized PersonaPlex (`brianmatzelle/personaplex-7b-v1-bnb-4bit`) on sub-12GB GPUs.
- Natural backend status now emits explicit low-VRAM messaging (for example: `Detected 8 GB VRAM → loading 4-bit PersonaPlex (low-VRAM mode)`).
- Omarchy daemon now supports low-VRAM mode via CLI/env and logs low-VRAM startup state.
- `scripts/clear-vram.sh` now aggressively clears CUDA-related cache directories in addition to torch cache flush.
- Version bumped to `2.9.6`.

### Notes
- v2.9.6 targets practical PersonaPlex quality on consumer GPUs like GTX 1070 Ti 8GB.

## [2.9.5] - 2026-02-24
### Added
- Added new CLI flag `--show-backend` to `voicedna speak` and `voicedna test-natural` for a large backend status banner.
- Added new one-line command `voicedna test-natural --dna-path ...` for instant natural backend testing.
- Added backend banner details: active backend, detected VRAM, and current consistency score.

### Changed
- Natural backend decision output is now highly prominent and color-coded (green for PersonaPlex, yellow for Piper/fallback).
- Added automatic fallback recommendation messaging: upgrade to 24GB+ VRAM or use cloud proxy for full PersonaPlex quality.
- Omarchy daemon now logs backend startup decision with backend + VRAM details on every startup.
- Updated `scripts/clear-vram.sh` to print free VRAM before and after cleanup.
- Omarchy docs/test flow now defaults to `voicedna test-natural --dna-path ...`.
- Version bumped to `2.9.5`.

### Notes
- v2.9.5 focuses on crystal-clear backend reporting for consumer GPUs while preserving high-VRAM PersonaPlex behavior.

## [2.9.4] - 2026-02-24
### Added
- Added new `PiperTTS` provider (`voicedna/providers/piper.py`) for lightweight natural voice synthesis on lower-VRAM systems.
- Added VRAM detection helpers in PersonaPlex provider and a configurable threshold (`VOICEDNA_MIN_PERSONAPLEX_VRAM_GB`, default `12GB`).
- Added CLI one-command natural test mode: `voicedna speak --test-natural ...` with forced playback and explicit backend-status messaging.
- Added helper script `scripts/clear-vram.sh` for quick GPU/system memory cleanup during local testing.

### Changed
- Natural backend resolution now uses VRAM-aware selection (`PersonaPlex` on high-VRAM, `Piper` fallback on consumer GPUs).
- `voicedna.synthesis.synthesize_and_process(...)` now auto-falls back from PersonaPlex to Piper (and to simple if Piper is unavailable).
- Omarchy daemon and PipeWire shim now support `auto` backend mode and natural backend auto-selection at startup.
- Omarchy test flow now uses `voicedna speak --test-natural --dna-path ...` for one-command verification.
- Version bumped to `2.9.4`.

### Notes
- v2.9.4 is tuned for real-world consumer hardware and works great on 8GB cards like GTX 1070 Ti when Piper is configured.

## [2.9.3] - 2026-02-24
### Added
- Added `audioop-lts` dependency for Python 3.13+ compatibility where stdlib `audioop` is removed.
- Added modern playback fallback via `sounddevice` in synthesis path.
- Added JUCE + VENOM VST3 starter scaffold for Reaper under `vst3/juce_venom_starter/` and `vst3/venom_bridge.py`.

### Changed
- Playback fallback chain now attempts `pydub` → `sounddevice` → `pw-play`/`aplay`.
- Omarchy docs/test flow updated to use new `voicedna speak` command path for natural synthesis testing.
- Version bumped to `2.9.3`.

### Notes
- v2.9.3 hardens modern Python playback reliability and starts practical VST3 testing path for Reaper.

## [2.9.2] - 2026-02-24
### Added
- New synthesis helper module `voicedna/synthesis.py` with backend resolution, provider dispatch, and audio playback helpers.
- New CLI command `voicedna verify-password --dna-path ...` for path/password checks before runtime speech.
- New `voicedna speak` options: `--natural-voice`, `--save-wav`, `--play/--no-play`.

### Changed
- `voicedna speak` now performs real text synthesis + full VoiceDNA processing chain, then optionally plays audio and/or saves WAV output.
- Omarchy test flow now exercises `voicedna speak --base-model personaplex --natural-voice` in `examples/omarchy/test-voicedna.sh`.
- Voice artifact creation flow is now standardized under `voices/` with explicit voice naming prompts in creation helpers.
- Version bumped to `2.9.2`.

### Notes
- PersonaPlex is now the effective default when `--natural-voice` is set or when running in Omarchy-like environments.

## [2.9.0] - 2026-02-24
### Added
- New optional PersonaPlex provider package `voicedna/providers` with `PersonaPlexTTS` backend support.
- New `VoiceDNAProcessor.synthesize_and_process(...)` path for text-to-speech provider integration before VoiceDNA filter processing.
- New Omarchy installer mode `--natural-voice` in `examples/omarchy/install-voicedna-omarchy.sh`.

### Changed
- Omarchy speech-dispatcher shim now supports backend selection and PersonaPlex text synthesis path.
- Omarchy daemon now supports `--tts-backend` / `VOICEDNA_TTS_BACKEND` and can probe PersonaPlex readiness.
- Version bumped to `2.9.0`.

### Notes
- PersonaPlex support is optional and designed to preserve simple CPU-first defaults while unlocking higher naturalness on capable hardware.

## [2.7.1] - 2026-02-24
### Added
- New Omarchy real-machine test helper: `examples/omarchy/test-voicedna.sh`.
- New Omarchy README section: `🔬 Quick Test on Your Real Omarchy Machine (5–10 minutes)` with exact verification commands.
- New installer `--test-mode` flow in `examples/omarchy/install-voicedna-omarchy.sh` that runs a 30-second smoke test sequence after install.

### Changed
- Omarchy installer now supports immediate end-to-end verification (birth if needed, notification speech, terminal speech, daemon status, consistency report output).
- Version bumped to `2.7.1`.

### Notes
- Added real-machine Omarchy test flow so you can verify desktop voice in minutes.

## [2.8.0] - 2026-02-24
### Added
- New optional `rvc` dependency extra in `pyproject.toml` for real Retrieval-based Voice Conversion runtime (`rvc-python`).
- New processor report status field `rvc_mode` for explicit RVC state tracking (`active`, `fallback`, `disabled`, `stub`).
- README section `🔊 Real Voice Cloning (RVC)` with setup keys for model and reference audio.

### Changed
- `ImprintConverterFilter` now supports real `imprint_converter.mode = "rvc"` execution path and calls `rvc_python` inference when configured.
- RVC path now includes robust fallback behavior plus explicit runtime setup messages when model/reference files are missing.
- Version bumped to `2.8.0`.

### Notes
- VoiceDNA now supports real optional cloning so your voice is literally you at every age.

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