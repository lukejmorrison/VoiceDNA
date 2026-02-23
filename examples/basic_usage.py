import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from voice_dna import VoiceDNA


def main():
    dna = VoiceDNA.create_new(
        "Luke Morrison's warm Canadian voice from 60-second recording",
        "luke",
    )
    dna.save("example.voicedna.json")

    print("Fingerprint:", dna.get_recognition_id())
    print(f"Age: {dna.get_current_age():.1f}")
    print("ElevenLabs prompt:", dna.generate_tts_prompt("elevenlabs"))
    print("Generic prompt:", dna.generate_tts_prompt("xtts"))


if __name__ == "__main__":
    main()
