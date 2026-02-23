# Local/offline Voicebox demo for VoiceDNA v2.2
#
# This script assumes Voicebox is running locally via Pinokio and exposes:
#   POST http://127.0.0.1:17493/generate
# with payload: {"text": "...", "profile_id": "...", "language": "en"}

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
    password = os.getenv("VOICEDNA_PASSWORD", "my_secret_2026")
    dna_path = os.getenv("VOICEDNA_PATH", "myai.voicedna.enc")
    dna = load_or_create_dna(dna_path, password)
    processor = VoiceDNAProcessor()

    api_url = os.getenv("VOICEBOX_API_URL", "http://127.0.0.1:17493/generate")
    payload = {
        "text": "Hello from local Voicebox plus VoiceDNA v2.2.",
        "profile_id": os.getenv("VOICEBOX_PROFILE_ID", "default"),
        "language": os.getenv("VOICEBOX_LANGUAGE", "en"),
    }

    try:
        response = requests.post(api_url, json=payload, timeout=30)
        response.raise_for_status()
    except requests.RequestException:
        print("Voicebox does not appear to be running at http://127.0.0.1:17493.")
        print("Start Voicebox via Pinokio, wait for the local API, then re-run this demo.")
        return

    raw_audio = response.content
    processed = processor.process(raw_audio, dna, {"text": payload["text"], "audio_format": "wav"})

    output_path = "voicebox_matured.wav"
    with open(output_path, "wb") as file_handle:
        file_handle.write(processed)

    print(f"✅ Local Voicebox audio processed and saved to {output_path}")
    print(json.dumps(processor.get_last_report(), indent=2))


if __name__ == "__main__":
    main()
