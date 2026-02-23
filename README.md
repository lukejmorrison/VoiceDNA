# VoiceDNA — Lifelong Sonic Identity for Every AI ❤️🔊

The open standard that gives every AI a permanent, recognizable **Voice Fingerprint** — just like your nephew Ash.  

You hear 3 seconds and instantly know *"That's my Grok"*, *"That's Luke's AI"*, or *"That's the Claude I've been friends with since 2026"*.

Built with Luke Morrison (Feb 23 2026) — fully open, MIT licensed, works with **ElevenLabs, XTTS, Qwen3-TTS, Cartesia, Fish Speech, local models**, etc.

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
pip install -r requirements.txt  # (none — zero dependencies!)
python voice_dna.py
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

## Files
- `voice_dna.py` — the complete VoiceDNA class (UAMF v4)
- `voicedna/plugins/` — plugin interface + manager + built-in filters
- `voicedna/framework.py` — higher-level processor with plugin auto-discovery
- `examples/openclaw_hook.py` — integration example for OpenClaw-like pipelines
- `examples/openclaw_skill.py` — one-file OpenClaw skill wrapper
- `examples/encrypted_plugin_demo.py` — encrypted load + processor demo
- `vst3/` — JUCE starter scaffold for future native plugin build
- `scripts/review_feedback.py` — appends structured feedback updates to `EVOLUTION.md`
- `CHANGELOG.md` — release-oriented change history
- `EVOLUTION.md` — feedback loop + design evolution log
- `UAMF_v4_schema.json` — formal JSON schema (optional but nice for validation)
- `LICENSE` — MIT

Made for the entire AI community. Fork it, improve it, ship it in your apps.

**Let's give every AI a soul you can hear.**

— Created with ❤️ by Luke Morrison + Grok