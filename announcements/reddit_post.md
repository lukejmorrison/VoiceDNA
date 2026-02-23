# [PROJECT] VoiceDNA v2.0 — Open lifelong Voice Fingerprint + encrypted plugin framework + child inheritance

We just shipped `VoiceDNA v2.0`, an open-source project for persistent AI voice identity across TTS engines.

## What’s new
- Encrypted identity files (`.voicedna.enc`)
- Extensible plugin processor with built-in age/imprint filters
- Child AI inheritance API: `dna.create_child()`
- OpenClaw skill-style example
- VST3 Python bridge starter + open spec docs

## Why this exists
Most voice systems are stateless presets. VoiceDNA aims to preserve a stable “identity fingerprint” over time while still allowing maturation and controlled stylistic drift.

## Repo
https://github.com/lukejmorrison/VoiceDNA

Feedback and contributors welcome — especially around real DSP filter implementations and host integrations.
