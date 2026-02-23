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

## Active Feedback Inputs Addressed
- Keep repo minimal and runnable.
- Keep zero-dependency runtime for core VoiceDNA.
- Add practical extension path for OpenClaw and future hosts.
- Make design evolution visible for contributors and future AI agents.

## Next Candidate Iterations
- Add optional encrypted VoiceDNA file support (feature-flagged, backwards compatible).
- Add package publishing workflow for PyPI.
- Add formal plugin compatibility contract tests.
- Add one-click "birth my AI" CLI flow.
