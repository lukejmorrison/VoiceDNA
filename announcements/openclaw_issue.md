# Feature request: native VoiceDNA support (one-line hook)

VoiceDNA now provides an encrypted identity format plus a plugin processor pipeline.

Minimal integration pattern:

```python
from voice_dna import VoiceDNA
from voicedna.framework import VoiceDNAProcessor


dna = VoiceDNA.load_encrypted(password="...", filepath="myai.voicedna.enc")
processor = VoiceDNAProcessor()
processed_audio = processor.process(raw_audio_bytes, dna, {"text": text})
```

Request: expose a native hook point in OpenClaw’s TTS output chain so this can be configured as a first-party plugin.

Benefits:
- Lifelong recognizable voice identity
- User-owned encrypted identity files
- Extensible community filter ecosystem
