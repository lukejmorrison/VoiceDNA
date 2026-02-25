# VoiceDNA VST3 Voice Genetics Foundation (v3.0.0)

This folder contains the first loadable JUCE VST3 foundation for Reaper/DAWs with a Python bridge into `VoiceDNAProcessor`.

## What is implemented now

- Real-time filter mode GUI controls:
	- Load `.voicedna` or `.voicedna.enc`
	- Age slider
	- Imprint strength slider
	- Bridge enable toggle
- Creation mode GUI controls:
	- Parent A / Parent B file pickers
	- Parent inheritance sliders (`Parent A %`, `Parent B %`)
	- Randomness slider
	- `Birth New Voice` button
- Lineage display placeholder (`Parent A × Parent B -> child`).
- Python runtime bridge script: `vst3/bridge_runtime.py`
	- `process` command calls `VoiceDNAProcessor` on WAV blocks.
	- `birth` command creates an encrypted child `.voicedna.enc` from two parent audio files.

## Build on Linux (Omarchy)

Prereqs:
- JUCE checkout path
- CMake 3.22+
- C++ toolchain (gcc/clang)
- Python env with VoiceDNA deps (`pip install -e .` in repo root)

```bash
cd /home/luke/dev/voiceDNA-codex
pip install -e .

cd vst3/juce_venom_starter
cmake -B build -S . -DJUCE_DIR=/absolute/path/to/JUCE
cmake --build build -j
```

Then copy the generated `.vst3` into your VST3 path and rescan in Reaper.

## Build on Windows

Prereqs:
- Visual Studio 2022 Build Tools (MSVC)
- CMake 3.22+
- JUCE checkout
- Python 3.10+ with VoiceDNA deps

```powershell
cd C:\path\to\voiceDNA-codex
py -m pip install -e .

cd vst3\juce_venom_starter
cmake -B build -S . -DJUCE_DIR=C:\path\to\JUCE
cmake --build build --config Release
```

## Reaper test flow (ASAP)

1. Add plugin to an audio track.
2. Set mode to `Real-time Filter`.
3. Load `.voicedna.enc`, set password, enable bridge.
4. Play audio to confirm bridge processing status updates.
5. Switch to `Create / Imprint`, select two parent audio files.
6. Click `Birth New Voice` and save child DNA output.

## Notes

- The bridge currently shells out to Python for per-block processing and is foundation-grade (functional, not low-latency optimized yet).
- Next pass should replace shell calls with a persistent Python/pybind11 bridge for production realtime performance.
