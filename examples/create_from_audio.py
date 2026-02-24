import argparse
import getpass
from pathlib import Path

from voice_dna import VoiceDNA


def main() -> int:
    parser = argparse.ArgumentParser(description="Create encrypted VoiceDNA from a local audio recording")
    parser.add_argument("--audio", required=True, help="Path to your voice recording (wav/mp3/m4a)")
    parser.add_argument("--user", default="luke", help="Identity/user name")
    parser.add_argument("--out", default="myai.voicedna.enc", help="Output encrypted VoiceDNA path")
    parser.add_argument("--password", default=None, help="Encryption password (omit to prompt)")
    args = parser.parse_args()

    audio_path = Path(args.audio).expanduser().resolve()
    if not audio_path.exists() or not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    password = args.password or getpass.getpass("VoiceDNA encryption password: ")
    if not password:
        raise ValueError("Password must not be empty")

    dna = VoiceDNA.create_new(str(audio_path), args.user)
    dna.save_encrypted(password=password, filepath=args.out)

    print(f"Created VoiceDNA: {dna.get_recognition_id()}")
    print(f"Encrypted file: {args.out}")
    print(f"Current age: {dna.get_current_age():.2f}")
    print("Prompt preview:", dna.generate_tts_prompt("xtts"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
