import json
import os
from pathlib import Path

import requests

from voice_dna import VoiceDNA
from voicedna import VoiceDNAProcessor


def load_or_create_dna(path: str, password: str) -> VoiceDNA:
    if Path(path).exists():
        return VoiceDNA.load_encrypted(password=password, filepath=path)

    dna = VoiceDNA.create_new("Luke Morrison's warm Canadian voice from 60-second recording", "luke")
    dna.save_encrypted(password=password, filepath=path)
    return dna


def main():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")
    if not api_key or not voice_id:
        print("Set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID before running this demo.")
        return

    password = os.getenv("VOICEDNA_PASSWORD", "my_secret_2026")
    dna_path = os.getenv("VOICEDNA_PATH", "myai.voicedna.enc")
    dna = load_or_create_dna(dna_path, password)
    processor = VoiceDNAProcessor()

    text = "Hello from VoiceDNA v2.2 with ElevenLabs integration."
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": api_key, "accept": "audio/wav", "Content-Type": "application/json"},
        json={"text": text, "model_id": os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")},
        timeout=45,
    )
    response.raise_for_status()

    processed = processor.process(response.content, dna, {"text": text, "audio_format": "wav"})
    with open("elevenlabs_matured.wav", "wb") as file_handle:
        file_handle.write(processed)

    print("✅ Saved ElevenLabs processed audio -> elevenlabs_matured.wav")
    print(json.dumps(processor.get_last_report(), indent=2))


if __name__ == "__main__":
    main()
