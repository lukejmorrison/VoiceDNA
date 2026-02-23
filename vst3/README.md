JUCE + VENOM starter for VoiceDNA VST3.

Python bridge ready:

`from vst3.python_bridge import VoiceDNA_VST_Bridge`

Compile with JUCE 8.
Open in Projucer, wire your DSP graph, and bridge VoiceDNA pipeline logic from `voicedna/framework.py`.

Starter files:
- `VoiceDNAProcessor.h`
- `python_bridge.py`
