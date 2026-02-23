import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from voice_dna import VoiceDNA
from voicedna import VoiceDNAProcessor
from voicedna.plugins import PromptTagFilter


def main():
    password = "my_secret_2026"
    path = "myai.voicedna.enc"

    dna = VoiceDNA.create_new("Luke Morrison's warm Canadian voice from 60-second recording", "luke")
    dna.save_encrypted(password=password, filepath=path)

    loaded = VoiceDNA.load_encrypted(password=password, filepath=path)
    processor = VoiceDNAProcessor()
    if not processor.filters:
        processor.register_filter(PromptTagFilter())

    print(f"Loaded encrypted VoiceDNA — Age: {loaded.get_current_age():.1f}")
    print("Active filters:", processor.get_filter_names())

    fake_audio = b"RAW_TTS_AUDIO_BYTES_HERE"
    processed = processor.process(fake_audio, loaded, {"base_model": "xtts", "prepend_style_tag": True})
    print(f"✅ Audio processed through plugin chain ({len(processed)} bytes)")


if __name__ == "__main__":
    main()
