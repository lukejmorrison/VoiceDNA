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
