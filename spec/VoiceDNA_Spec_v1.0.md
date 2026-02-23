# VoiceDNA Open Standard v1.0

Any voice engine may implement this contract:

```python
from voice_dna import VoiceDNA
from voicedna.framework import VoiceDNAProcessor


def apply_voicedna(audio_bytes: bytes, dna_path: str, password: str | None = None) -> bytes:
    if password is None:
        raise ValueError("Password is required for encrypted VoiceDNA")
    dna = VoiceDNA.load_encrypted(password=password, filepath=dna_path)
    processor = VoiceDNAProcessor()
    return processor.process(audio_bytes, dna)
```

This enables direct integration into Grok Voice Agent, OpenClaw, Cartesia, and future TTS pipelines.
