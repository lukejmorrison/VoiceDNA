import argparse
import getpass
import re
from pathlib import Path

from voice_dna import VoiceDNA


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "voice"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create encrypted VoiceDNA from a local audio recording")
    parser.add_argument("--audio", required=True, help="Path to your voice recording (wav/mp3/m4a)")
    parser.add_argument("--voice-name", default="", help="Human-friendly voice name (prompts if omitted)")
    parser.add_argument("--user", default="", help="Identity/user name (defaults to voice name slug)")
    parser.add_argument("--out", default="", help="Output file name (always written inside voices/)")
    parser.add_argument("--password", default=None, help="Encryption password (omit to prompt)")
    args = parser.parse_args()

    audio_path = Path(args.audio).expanduser().resolve()
    if not audio_path.exists() or not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    voice_name = args.voice_name.strip() or input("Voice name: ").strip()
    if not voice_name:
        raise ValueError("Voice name must not be empty")

    voice_slug = _slugify(voice_name)
    resolved_user = args.user.strip() or voice_slug

    voices_dir = Path("voices")
    voices_dir.mkdir(parents=True, exist_ok=True)

    file_name = Path(args.out).name if args.out else f"{voice_slug}.voicedna.enc"
    if not file_name.endswith(".voicedna.enc"):
        file_name = f"{file_name}.voicedna.enc"
    output_path = voices_dir / file_name

    password = args.password or getpass.getpass("VoiceDNA encryption password: ")
    if not password:
        raise ValueError("Password must not be empty")

    if args.password is None:
        confirm_password = getpass.getpass("Confirm encryption password: ")
        if password != confirm_password:
            raise ValueError("Passwords do not match")

    dna = VoiceDNA.create_new(str(audio_path), resolved_user)
    dna.save_encrypted(password=password, filepath=str(output_path))

    print(f"Created VoiceDNA: {dna.get_recognition_id()}")
    print(f"Encrypted file: {output_path}")
    print(f"Current age: {dna.get_current_age():.2f}")
    print("Prompt preview:", dna.generate_tts_prompt("xtts"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
