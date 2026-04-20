# AGENTS.md — VoiceDNA

## Scope
Lifelong sonic identity SDK published to PyPI (`pip install voicedna`). TTS backends, per-agent voice presets, voice cloning, speaker consistency, VST3 plugin.

## Agent Assignment
- **Dr Voss Thorne** — voice science, acoustic research, imprint design
- **Namshub** — OpenClaw integration, adapter wiring, CI/CD, testing

## Rules
- This is a published PyPI package — changes must pass all 31+ tests before merge
- Per-agent voice presets live in `openclaw/skills/voicedna-agent-voices/`, not here
- The `VoiceAdapter` class is the integration surface with OpenClaw
- Use repo-local venv (`python -m venv .venv`)
- Follow the fix-or-feature doc discipline
