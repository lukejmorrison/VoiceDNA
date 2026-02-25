# VoiceDNA VST3 Starter (JUCE + VENOM) for Reaper

This folder includes a pre-built starter scaffold for building a VoiceDNA VST3 plugin and testing it in Reaper.

## Included

- `juce_venom_starter/` — JUCE CMake project skeleton for VST3 plugin build
	- `CMakeLists.txt`
	- `Source/PluginProcessor.h`
	- `Source/PluginProcessor.cpp`
	- `Source/PluginEditor.h`
	- `Source/PluginEditor.cpp`
- `venom_bridge.py` — Python VENOM bridge that loads encrypted VoiceDNA and processes audio bytes
- `python_bridge.py` — original minimal Python bridge (kept for compatibility)
- `VoiceDNAProcessor.h` — legacy placeholder header

## Build for Reaper (Linux example)

```bash
cd vst3/juce_venom_starter
cmake -B build -S . -DJUCE_DIR=/absolute/path/to/JUCE
cmake --build build -j
```

Copy resulting `.vst3` into your Reaper VST3 path and rescan plugins.

## VENOM Bridge Flow

Use `venom_bridge.py` inside your plugin host bridge layer:

1. load encrypted DNA (`voices/<name>.voicedna.enc`)
2. send audio bytes to `VoiceDNAVenomBridge.process_pcm_bytes(...)`
3. write processed bytes back into plugin buffer
4. inspect processor report with `get_last_report()`

This gives you a practical launchpad for Reaper + VoiceDNA integration without reworking core package architecture.
