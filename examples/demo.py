import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from voice_dna import VoiceDNA


def main():
    dna = VoiceDNA.create_new(
        "Luke Morrison's warm Canadian voice from 60-second recording",
        "luke",
    )
    dna.save("demo.voicedna.json")

    loaded = VoiceDNA.load("demo.voicedna.json")
    loaded.evolve(days_passed=7)

    print("Fingerprint:", loaded.get_recognition_id())
    print(f"Age after evolve: {loaded.get_current_age():.1f}")
    print("ElevenLabs prompt:", loaded.generate_tts_prompt("elevenlabs"))


if __name__ == "__main__":
    main()
