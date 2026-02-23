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
    api_key = os.getenv("CARTESIA_API_KEY")
    api_url = os.getenv("CARTESIA_API_URL", "https://api.cartesia.ai/tts")
    voice_id = os.getenv("CARTESIA_VOICE_ID")

    if not api_key or not voice_id:
        print("Set CARTESIA_API_KEY and CARTESIA_VOICE_ID before running this demo.")
        return

    password = os.getenv("VOICEDNA_PASSWORD", "my_secret_2026")
    dna_path = os.getenv("VOICEDNA_PATH", "myai.voicedna.enc")
    dna = load_or_create_dna(dna_path, password)
    processor = VoiceDNAProcessor()

    text = "Hello from VoiceDNA v2.2 with Cartesia integration."
    response = requests.post(
        api_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "audio/wav",
            "Content-Type": "application/json",
        },
        json={
            "text": text,
            "voice_id": voice_id,
            "model": os.getenv("CARTESIA_MODEL", "sonic-english"),
        },
        timeout=45,
    )
    response.raise_for_status()

    processed = processor.process(response.content, dna, {"text": text, "audio_format": "wav"})
    with open("cartesia_matured.wav", "wb") as file_handle:
        file_handle.write(processed)

    print("✅ Saved Cartesia processed audio -> cartesia_matured.wav")
    print(json.dumps(processor.get_last_report(), indent=2))


if __name__ == "__main__":
    main()
