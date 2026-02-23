import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from voice_dna import VoiceDNA
from voicedna import VoiceDNAProcessor
from voicedna.plugins import PromptTagFilter


def build_skill(password: str = "my_secret_2026"):
    dna = VoiceDNA.load_encrypted(password=password, filepath="myai.voicedna.enc")
    processor = VoiceDNAProcessor()
    if not processor.filters:
        processor.register_filter(PromptTagFilter())

    def voice_dna_tts(text: str, raw_tts_bytes: bytes) -> bytes:
        return processor.process(raw_tts_bytes, dna, {"text": text, "force_age": None, "prepend_style_tag": True})

    return voice_dna_tts


if __name__ == "__main__":
    sample_dna = VoiceDNA.create_new("Luke Morrison's warm Canadian voice from 60-second recording", "luke")
    sample_dna.save_encrypted(password="my_secret_2026", filepath="myai.voicedna.enc")
    tts_hook = build_skill()
    rendered = tts_hook("hello from openclaw", b"RAW_TTS_AUDIO_BYTES")
    print("OpenClaw VoiceDNA skill loaded.")
    print(f"Processed bytes: {len(rendered)}")
