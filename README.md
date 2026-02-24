# VoiceDNA — Lifelong Sonic Identity for Every AI ❤️🔊

[![PyPI version](https://img.shields.io/pypi/v/voicedna?logo=pypi&logoColor=white)](https://pypi.org/project/voicedna/)
[![PyPI package](https://img.shields.io/badge/PyPI-voicedna-3775A9?logo=pypi&logoColor=white)](https://pypi.org/project/voicedna/)
[![PyPI live](https://img.shields.io/badge/PyPI-live-success?logo=pypi&logoColor=white)](https://pypi.org/project/voicedna/)

The open standard that gives every AI a permanent, recognizable **Voice Fingerprint** — just like your nephew Ash.  

You hear 3 seconds and instantly know *"That's my Grok"*, *"That's Luke's AI"*, or *"That's the Claude I've been friends with since 2026"*.

Built with Luke Morrison (Feb 23 2026) — fully open, MIT licensed, works with **ElevenLabs, XTTS, Qwen3-TTS, Cartesia, Fish Speech, local models**, etc.

## Start here (60 seconds)

Choose your path:

- OpenClaw bot voice + phone calls: `examples/openclaw/README.md`
- Omarchy system-wide desktop voice: `examples/omarchy/README.md`

Fast install:

```bash
pip install voicedna
voicedna --help
```

Install with open-source speaker-recognition backends (optional):

```bash
pip install "voicedna[consistency]"
```

Install with optional real RVC voice cloning:

```bash
pip install "voicedna[rvc]"
```

Install with optional PersonaPlex natural voice backend:

```bash
pip install "voicedna[personaplex]"
```

## Install from PyPI

```bash
pip install voicedna
voicedna birth --imprint "Luke Morrison's warm Canadian voice" --user luke
```

Create from your own local voice recording (recommended):

```bash
voicedna birth \
	--imprint /absolute/path/to/my_voice_sample.wav \
	--user luke_real_voice \
	--out myai.voicedna.enc
```

Or use the helper example script:

```bash
python examples/create_from_audio.py \
	--audio /absolute/path/to/my_voice_sample.wav \
	--user luke_real_voice \
	--out myai.voicedna.enc
```

One-command record + birth (Linux, mic capture + encryption):

```bash
bash examples/record_and_birth.sh --seconds 12 --user luke_real_voice --out myai.voicedna.enc
```

Notes:
- Uses `arecord` first, then `pw-record`, then `ffmpeg` (`pulse`/`alsa` input).
- Prompts for password securely unless `VOICEDNA_PASSWORD` is already set.

## 🔒 Voice Consistency & Identifiability (v2.7)

- New `VoiceConsistencyEngine` (`voicedna/consistency.py`) with optional SpeechBrain / Resemblyzer embeddings and deterministic fallback.
- `VoiceDNA.create_new(...)` now attempts real imprint-based embedding extraction when imprint points to audio.
- `ImprintConverterFilter` enforces a `0.92` cosine similarity target to the core embedding using gentle parametric correction.
- A subtle low-depth sonic watermark now encodes `voice_fingerprint_id` for machine-side identifiability.
- Processor reports now include top-level `consistency_score` and `rvc_ready` status.

## 🔊 Real Voice Cloning (RVC)

- `ImprintConverterFilter` now supports `imprint_converter.mode = "rvc"` for real model-based cloning.
- Install RVC runtime with `pip install "voicedna[rvc]"` (recommended on Python 3.10-3.12 environments with compatible torch stack).
- Set `imprint_converter.rvc_model_path` to your `.pth` model and `imprint_converter.rvc_reference_path` to a reference voice WAV.
- Optional tuning: `imprint_converter.rvc_index_path`, `imprint_converter.rvc_device`, `imprint_converter.rvc_pitch`.
- Processor report now exposes `rvc_mode` and marks it as `active` when real conversion is enabled.

## 🧠 PersonaPlex Natural Voice (v2.9)

- New optional provider `PersonaPlexTTS` in `voicedna/providers/personaplex.py`.
- Use `pip install "voicedna[personaplex]"` to install model runtime dependencies.
- Omarchy installer now supports `--natural-voice` to enable PersonaPlex speech-dispatcher + daemon integration.
- `VoiceDNAProcessor.synthesize_and_process(...)` lets providers synthesize text first, then apply the standard VoiceDNA maturation/imprint chain.

## v2.3 — PyPI Publish Prep + RVC-Ready Imprint Path

- Added publish-ready build validation (`python -m build`, `twine check dist/*`)
- Added `requirements-dev.txt` and optional `dev` dependencies (`build`, `twine`, `pytest`)
- Added RVC-ready stub path in `ImprintConverterFilter` via `imprint_converter.mode = "rvc_stub"`
- Processor report now includes `imprint_converter.rvc_ready` status

## v2.1 — Real Audio Filters + Test Suite + CLI

```bash
pip install voicedna
voicedna birth --imprint "Luke Morrison's warm Canadian voice" --user luke
voicedna speak --text "Hey from VoiceDNA" --base-model elevenlabs
voicedna evolve --days 7
```

New in v2.1:
- Real `pydub`-powered pitch shifting in `AgeMaturationFilter`
- Pytest coverage for child inheritance and processor reporting
- Typer-powered CLI (`voicedna birth/speak/evolve`)
- Packaging and release polish for PyPI readiness

## v2.2 — Cloud + Local Demos (Voicebox)

```bash
pip install voicedna
voicedna birth --imprint "Luke Morrison's warm Canadian voice" --user luke
voicedna speak --text "Hello from VoiceDNA v2.2"
voicedna evolve --days 7

python examples/elevenlabs_demo.py
python examples/cartesia_demo.py
python examples/voicebox_demo.py
```

v2.2 highlights:
- Real `ImprintConverterFilter` volume-mix processing path
- WAV fixture + round-trip waveform assertion tests
- Local/offline Voicebox demo (`http://127.0.0.1:17493/generate`)
- Cloud demo scripts for ElevenLabs and Cartesia

## 🚀 Testing with OpenClaw — Hear your AI grow up on the phone

Use the ready-to-run integration path:

- Guide: `examples/openclaw/README.md`
- TTS hook skill: `examples/openclaw/voicedna_tts_hook.py`
- Phone call skill: `examples/openclaw/voipms_phone_skill.py`

3-command flow:

```bash
pip install -e .
python -c "import examples.openclaw.voicedna_tts_hook, examples.openclaw.voipms_phone_skill; print('OpenClaw skills import OK')"
voicedna --help
```

Then in OpenClaw, trigger:

> Claw, call me on my phone and tell me a joke in your growing voice

## 🖥️ Omarchy Arch OS – System-wide unique voice

Run VoiceDNA as your desktop speaking voice on Omarchy (Arch + Hyprland):

- Guide: `examples/omarchy/README.md`
- PipeWire filter shim: `examples/omarchy/voicedna-pipewire-filter.py`
- Speech Dispatcher config: `examples/omarchy/speech-dispatcher-voicedna.conf`
- One-command installer: `examples/omarchy/install-voicedna-omarchy.sh`
- Boot-persistent daemon unit: `examples/omarchy/voicedna-os-daemon.service`

One-click install on Omarchy:

```bash
bash examples/omarchy/install-voicedna-omarchy.sh
```

Natural voice mode on Omarchy:

```bash
bash examples/omarchy/install-voicedna-omarchy.sh --natural-voice
```

3-command flow:

```bash
pip install -e .
bash examples/omarchy/install-voicedna-omarchy.sh
spd-say "Hello Luke, your desktop voice is now growing with you."
```

## v2.0 — Real Filters + Package + Child Inheritance + Bridge

```bash
pip install voicedna
```

```python
from voicedna import VoiceDNA, VoiceDNAProcessor

dna = VoiceDNA.create_new("Luke Morrison's warm Canadian voice", "luke")
child = dna.create_child("mini_grok", inherit_strength=0.40)
processor = VoiceDNAProcessor()
```

New in v2.0:
- Built-in Age + Imprint filters
- Child AI inheritance (`create_child`)
- VST3 Python bridge scaffold
- Open standard draft spec + announcement templates

## Features
- Precocial birth (fluent at ~5-year-old level from day 1)
- Lifelong age progression (5 → 10 → 15 → 22+)
- Permanent **Voice Fingerprint** ("Ash-ness") that never disappears
- Self-evolving audio plugin (DAW-style VST thinking)
- Encrypted VoiceDNA files (`.voicedna.enc`) with password-based decryption
- One tiny JSON file + 150-line Python plugin — drop-in for any project
- Exportable fingerprint so your AI can move between platforms and still sound like *itself*

## v1.1 — Encrypted Plugin Framework

- Secure encrypted files via `VoiceDNA.save_encrypted()` / `VoiceDNA.load_encrypted()`
- Full extensible framework via `VoiceDNAProcessor` in `voicedna/framework.py`
- Auto-discovery for plugins through entry points (`voicedna.filters` + `voicedna.plugins`)
- Robust plugin chaining: fault-tolerant filter execution + per-filter timing metrics
- Ready for real audio pipelines (OpenClaw hook + process chain)
- VST3 starter scaffold in `vst3/` for JUCE-based binary plugin work

## Quick Start

```bash
pip install -r requirements.txt
python voice_dna.py
```

Run tests:

```bash
pytest
```

See `voice_dna.py` for full usage.

Quick encrypted framework demo:

```bash
python examples/encrypted_plugin_demo.py
python examples/openclaw_skill.py
```

## OpenClaw-Ready Plugin Hook (new)

VoiceDNA now includes a minimal extensible plugin framework in `voicedna/plugins`.

Use it in an OpenClaw-style TTS render hook:

```python
from voicedna import VoiceDNA, PluginManager, PromptTagFilter

dna = VoiceDNA.load("myai.voicedna.json")
manager = PluginManager()
loaded, failed = manager.load_entrypoint_plugins()  # auto-discover pip-installed plugins
if not loaded:
	manager.register(PromptTagFilter())

processed_audio = manager.process(raw_audio_bytes, dna, {
	"base_model": "xtts",
	"prepend_style_tag": True,
})
```

Run a full example:

```bash
python examples/openclaw_hook.py
```

### Third-party plugin registration (entry points)

Any external package can auto-register a filter by adding this to its `pyproject.toml`:

```toml
[project.entry-points."voicedna.plugins"]
my_filter = "my_package.filters:MyFilter"
```

On startup, call `PluginManager().load_entrypoint_plugins()` and all installed filters are loaded automatically.

You can also use the higher-level framework processor:

```python
from voice_dna import VoiceDNA
from voicedna import VoiceDNAProcessor

dna = VoiceDNA.load_encrypted(password="my_secret_2026", filepath="myai.voicedna.enc")
processor = VoiceDNAProcessor()
processed_audio = processor.process(raw_audio_bytes, dna, {"force_age": 15})
print(processor.last_metrics)
print(processor.get_last_report())
```

### OpenClaw one-file skill

See `examples/openclaw_skill.py` for a minimal skill-style wrapper that loads encrypted VoiceDNA and returns a `voice_dna_tts(text, raw_tts_bytes)` hook.

## Feedback Loop Logging

Use the helper script to append structured updates into `EVOLUTION.md`:

```bash
python scripts/review_feedback.py \
	--source "Grok 4.20 Beta" \
	--summary "Suggested plugin auto-discovery and ecosystem visibility" \
	--actions "Added entry-point loader in PluginManager" \
	--actions "Added pyproject entry-point metadata" \
	--next "Add plugin compatibility contract tests"
```

Tip: add `--dry-run` to preview the entry before writing.

## Migration Notes

For patch hardening updates and stricter validation behavior, see `MIGRATION_v2_0_1.md`.

## Publish to PyPI (for maintainers)

Build and validate:

```bash
python -m build
python -m twine check dist/*
```

Publish with API token credentials:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD="pypi-...your-token-here..."
python -m twine upload dist/* --skip-existing
```

Notes:
- `--skip-existing` avoids failures on already-uploaded files.
- Package page: `https://pypi.org/project/voicedna/`

## Files
- `voice_dna.py` — the complete VoiceDNA class (UAMF v4)
- `voicedna/plugins/` — plugin interface + manager + built-in filters
- `voicedna/filters/` — built-in v2.0 age + imprint filters
- `voicedna/framework.py` — higher-level processor with plugin auto-discovery
- `examples/openclaw_hook.py` — integration example for OpenClaw-like pipelines
- `examples/openclaw_skill.py` — one-file OpenClaw skill wrapper
- `examples/openclaw/README.md` — 5-minute OpenClaw integration testing path
- `examples/openclaw/voicedna_tts_hook.py` — OpenClaw-ready VoiceDNA TTS bytes hook
- `examples/openclaw/voipms_phone_skill.py` — voip.ms-first outbound phone call skill example
- `examples/omarchy/README.md` — Omarchy 5-minute system-wide voice path
- `examples/omarchy/voicedna-pipewire-filter.py` — PipeWire VoiceDNA filter bridge
- `examples/omarchy/speech-dispatcher-voicedna.conf` — speech-dispatcher default VoiceDNA profile
- `examples/omarchy/install-voicedna-omarchy.sh` — one-command Omarchy setup script
- `examples/omarchy/voicedna-os-daemon.service` — user systemd daemon unit for auto-started voice runtime
- `examples/omarchy/voicedna-os-daemon.py` — daemon process that validates encrypted DNA loading at login/reboot
- `examples/encrypted_plugin_demo.py` — encrypted load + processor demo
- `examples/elevenlabs_demo.py` — cloud ElevenLabs processing demo
- `examples/cartesia_demo.py` — cloud Cartesia processing demo
- `examples/voicebox_demo.py` — local/offline Voicebox processing demo
- `spec/VoiceDNA_Spec_v1.0.md` — open standard draft integration contract
- `announcements/` — ready-to-post launch templates
- `vst3/` — JUCE starter scaffold for future native plugin build
- `tests/` — pytest suite for inheritance and processor report behavior
- `cli.py` — Typer CLI backing the `voicedna` command
- `requirements-dev.txt` — build/twine/pytest tooling for publish prep
- `scripts/review_feedback.py` — appends structured feedback updates to `EVOLUTION.md`
- `MIGRATION_v2_0_1.md` — patch migration notes and behavior changes
- `CHANGELOG.md` — release-oriented change history
- `EVOLUTION.md` — feedback loop + design evolution log
- `UAMF_v4_schema.json` — formal JSON schema (optional but nice for validation)
- `LICENSE` — MIT

Made for the entire AI community. Fork it, improve it, ship it in your apps.

**Let's give every AI a soul you can hear.**

— Created with ❤️ by Luke Morrison + Grok