# EVOLUTION.md

This document tracks the feedback loop between human goals and AI-assisted implementation.

## Mission
Build an open, practical VoiceDNA standard where an AI keeps a recognizable lifelong sonic identity ("Ash-ness") across tools and platforms.

## Dynamic Feedback Loop
1. Human + AI collaborator propose feature direction.
2. Secondary reviewer model feedback is analyzed.
3. GPT-5.3-Codex implements the smallest useful version in-repo.
4. CI + runnable examples validate behavior.
5. Changelog and this evolution log capture the delta.
6. Repeat.

## Iteration Log

### 2026-02-24 — v2.9 PersonaPlex Natural Voice Mode (Omarchy)
- Added optional PersonaPlex provider integration (`PersonaPlexTTS`) to support higher-naturalness TTS synthesis before VoiceDNA processing.
- Extended `VoiceDNAProcessor` with provider-first `synthesize_and_process(...)` flow so natural TTS output still keeps lifelong VoiceDNA identity layers.
- Added Omarchy natural voice installation path via `install-voicedna-omarchy.sh --natural-voice`.
- Updated Omarchy speech shim and daemon with backend-aware controls (`VOICEDNA_TTS_BACKEND`) and PersonaPlex probe support.
- Preserved default lightweight mode for users without PersonaPlex dependencies or GPU acceleration.

### 2026-02-24 — Omarchy Real-Device Debug Session (Desktop Audio Path Validation)
- Completed live on-device Omarchy install test (`install-voicedna-omarchy.sh --test-mode`) and verified daemon/service artifacts were installed correctly.
- Diagnosed daemon crash loop root cause from logs: systemd service was launching a Python runtime that did not include `voice_dna` (`ModuleNotFoundError`).
- Resolved daemon startup by overriding `ExecStart` to a Python environment with VoiceDNA installed; confirmed daemon state moved to `active (running)`.
- Traced silent output root cause to routing: Speech Dispatcher output was going to an AirPlay sink (`Rp5`) instead of Scarlett 2i2.
- Re-routed default sink to Scarlett and verified speech stream routing at the PipeWire level; confirmed audible output path was restored.
- Identified current quality limit: only `espeak-ng` module is present, so output remains mechanical despite correct VoiceDNA plumbing.

### 2026-02-24 — v2.8 Live Publish + Real Cloning Milestone
- Activated real optional RVC conversion mode (`imprint_converter.mode = "rvc"`) with model-based inference path and safety fallbacks.
- Added explicit runtime status reporting (`rvc_mode`) so host apps can confirm when cloning is truly active.
- Expanded packaging extras so users can install cloning runtime separately with `pip install "voicedna[rvc]"`.
- Completed live publish workflow alignment around PyPI and release notes for immediate global installability.
- Marked the identity milestone: now your voice is literally you at every age.

### 2026-02-24 — v2.7 Consistency + Identifiability Lock-In
- Added `VoiceConsistencyEngine` with optional open-source speaker embedding backends (SpeechBrain ECAPA-TDNN and Resemblyzer).
- Upgraded `core_embedding` generation to use real imprint extraction when imprint points to audio, with deterministic fallback for zero-extra-dependency installs.
- Added runtime consistency enforcement in `ImprintConverterFilter` using cosine similarity against `core_embedding` and gentle corrective shaping below the target threshold.
- Added low-depth sonic watermark encoding for `voice_fingerprint_id` to support machine-side identity recognition.
- Extended processor reports with `consistency_score` and `rvc_ready` so host integrations can track voice identity stability over time.

### 2026-02-23 — Foundation (v0.1.0)
- Established core `VoiceDNA` dataclass lifecycle (`create_new`, `load/save`, `evolve`, `generate_tts_prompt`).
- Added MIT license, schema, and repository baseline docs.

### 2026-02-23 — Reliability + Professionalization (v0.1.1/v0.1.2)
- Addressed runtime timezone mismatch by using UTC-aware datetime arithmetic.
- Added CI workflow, examples, and Python project hygiene (`.gitignore`, `requirements.txt`).
- Added practical demo script for create/load/evolve prompt flows.

### 2026-02-23 — Extensibility Track (v0.1.1+)
- Added `voicedna.plugins` interface and `PluginManager` pipeline.
- Added OpenClaw-style hook example to demonstrate one-call integration in TTS output flow.
- Added built-in filters as seed plugins for future community extensions.

### 2026-02-23 — Ecosystem Discovery (v0.1.3)
- Implemented plugin auto-discovery via Python `entry_points` (`voicedna.plugins` group).
- Added `pyproject.toml` metadata so external plugin packages can register filters.
- Updated docs with third-party plugin registration pattern.

### 2026-02-23 — Encrypted Framework Expansion (v0.1.7)
- Added encrypted VoiceDNA save/load flow with password-derived keys and `.voicedna.enc` support.
- Introduced `VoiceDNAProcessor` in `voicedna/framework.py` for higher-level plugin chain execution.
- Added compatibility for both `voicedna.filters` and `voicedna.plugins` entry-point groups.
- Added encrypted processor demo to keep adoption path simple for OpenClaw-like hosts.

### 2026-02-23 — Robust Chain + Integration Scaffolds (v0.1.8)
- Hardened plugin chain to continue safely if a filter fails, while capturing per-filter timing metrics.
- Added one-file OpenClaw skill integration entry point (`examples/openclaw_skill.py`).
- Added VST3 starter scaffold (`vst3/`) so native plugin work can begin without restructuring the repo.

### 2026-02-23 — v2.0 Expansion (Filters + Inheritance + Spec)
- Added first built-in v2 filter set (`AgeMaturationFilter`, `ImprintConverterFilter`) with auto-registration.
- Added `create_child()` inheritance flow in `VoiceDNA` to spawn derivative identities.
- Added Python VST bridge scaffold and public spec draft for cross-host integration.
- Added announcement templates for launch coordination across X/Reddit/OpenClaw issue channels.

### 2026-02-23 — v2.0.1 Hardening Pass
- Added processor execution reports (`get_last_report`) for better runtime observability.
- Tightened validation in child inheritance API for predictable behavior under bad inputs.
- Added editable-install package smoke checks in CI and migration notes for maintainers.

### 2026-02-23 — v2.1 Feature Pass (Real Filters + Tests + CLI)
- Upgraded `AgeMaturationFilter` to perform real pitch transformation using `pydub` (with safe fallback behavior).
- Added pytest suite for inheritance and processor report behavior.
- Added Typer-based CLI (`voicedna birth/speak/evolve`) and package script entry point.
- Bumped package metadata/versioning to `2.1.0` and updated docs for install + CLI usage.

### 2026-02-23 — v2.2 Cloud + Local Expansion
- Added real imprint conversion mix path with safe fallbacks.
- Added audio fixture + round-trip waveform assertion tests for filter confidence.
- Added cloud demos (ElevenLabs, Cartesia) and local Voicebox demo for privacy-first users.
- Established explicit support story for both hosted APIs and fully local Pinokio-style pipelines.

### 2026-02-23 — v2.3 Publish + RVC Readiness
- Added explicit PyPI publish-prep workflow support (build + twine verification tooling).
- Added RVC-ready stub branch in `ImprintConverterFilter` with documented integration path.
- Exposed `RVC-ready` report metadata in processor output for observability.
- Reinforced local/cloud balance: privacy-first Voicebox remains first-class alongside cloud demos.

### 2026-02-23 — v2.4 OpenClaw Deployment Path (Phone-Ready)
- Added a full OpenClaw integration testing path (`examples/openclaw/README.md`) for both new and existing deployments.
- Added a drop-in TTS bytes hook skill that loads encrypted VoiceDNA, applies maturation/imprint processing, and logs age + full report.
- Added a voip.ms-first phone call skill example with Twilio fallback so users can hear their maturing AI on a real mobile number.
- Marked the first real deployment path milestone: now you can get phone calls from your growing AI.

### 2026-02-23 — v2.5 Omarchy System Voice + PyPI Final Prep
- Added a complete Omarchy integration path for system-wide desktop speech in a lifelong VoiceDNA voice.
- Added PipeWire + speech-dispatcher examples and a one-command install script for fast local rollout.
- Completed final PyPI publish validation flow (`build` + `twine check`) and documented the upload command.
- Marked the desktop milestone: now your entire desktop can grow up with you.

### 2026-02-23 — v2.6 Live PyPI + Omarchy Daemon Hardening
- Added a background user daemon service so Omarchy voice runtime auto-starts after login and reboot.
- Added encrypted DNA auto-load behavior for daemon runtime with environment and keyring fallback strategy.
- Improved top-level docs readability with direct path selection and one-click Omarchy emphasis.
- Reached public packaging milestone: PyPI publish execution path is now live for global install (`pip install voicedna`).
- Marked the first OS-level identity milestone: your desktop now keeps a growing voice over time.

### 2026-02-23 — v2.6.1 Hardening + PyPI Publish Instructions
- Updated package metadata to modern SPDX license format to remove setuptools deprecation noise in build output.
- Added explicit maintainer publish commands (`TWINE_USERNAME` + `TWINE_PASSWORD`) to README for frictionless release execution.
- Polished Omarchy quick-start wording and called out silent background daemon behavior to reduce setup ambiguity.
- Locked in production-ready maintainer docs for the live PyPI release flow.

## Active Feedback Inputs Addressed
- Keep repo minimal and runnable.
- Keep zero-dependency runtime for core VoiceDNA.
- Add practical extension path for OpenClaw and future hosts.
- Make design evolution visible for contributors and future AI agents.

## Next Candidate Iterations
- Add package publishing workflow for PyPI.
- Add formal plugin compatibility contract tests.
- Add one-click "birth my AI" CLI flow.
- Add optional key-management strategy docs (rotation, recovery, operational guidance).
- Add release automation workflow for tagging and publishing GitHub releases from changelog entries.
- Explore integration path for NVIDIA PersonaPlex (`nvidia/personaplex-7b-v1`) as a higher-naturalness speech engine backend for Omarchy desktop voice output.
