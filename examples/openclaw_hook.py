import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from voicedna import Base64PassThroughFilter, PluginManager, PromptTagFilter, VoiceDNA


def openclaw_render_hook(raw_audio_bytes: bytes, dna: VoiceDNA) -> bytes:
    manager = PluginManager()
    manager.register(PromptTagFilter())
    manager.register(Base64PassThroughFilter())

    return manager.process(
        raw_audio_bytes,
        dna,
        {
            "base_model": "xtts",
            "prepend_style_tag": True,
            "round_trip_base64": False,
        },
    )


def main():
    dna = VoiceDNA.create_new("Luke Morrison's warm Canadian voice from 60-second recording", "luke")
    mock_audio = b"RAW_TTS_AUDIO_BYTES"
    processed = openclaw_render_hook(mock_audio, dna)

    print("Plugins applied in OpenClaw hook")
    print("Input bytes:", mock_audio)
    print("Output bytes:", processed)


if __name__ == "__main__":
    main()
