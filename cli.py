import json
import re
from pathlib import Path

import typer
from cryptography.fernet import InvalidToken

from voice_dna import VoiceDNA
from voicedna import VoiceDNAProcessor


app = typer.Typer(help="VoiceDNA command line interface")
VOICES_DIR = Path("voices")


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "voice"


def _ensure_voices_dir() -> Path:
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    return VOICES_DIR


def _build_voice_path(voice_name: str, out: str | None = None) -> Path:
    voices_dir = _ensure_voices_dir()
    if out:
        file_name = Path(out).name
    else:
        file_name = f"{_slugify(voice_name)}.voicedna.enc"

    if not file_name.endswith(".voicedna.enc"):
        file_name = f"{file_name}.voicedna.enc"
    return voices_dir / file_name


def _resolve_dna_path(dna_path: str) -> str:
    candidate = Path(dna_path)
    if candidate.exists():
        return str(candidate)

    voices_candidate = VOICES_DIR / dna_path
    if voices_candidate.exists():
        return str(voices_candidate)

    if not dna_path.endswith(".voicedna.enc"):
        named_candidate = VOICES_DIR / f"{dna_path}.voicedna.enc"
        if named_candidate.exists():
            return str(named_candidate)

    return dna_path


def _load_encrypted_or_exit(password: str, dna_path: str) -> VoiceDNA:
    resolved_path = _resolve_dna_path(dna_path)
    try:
        return VoiceDNA.load_encrypted(password=password, filepath=resolved_path)
    except FileNotFoundError:
        typer.secho(
            f"Encrypted VoiceDNA file not found: {dna_path}\n"
            "Tip: pass the correct path with --dna-path or use a voice name stored in voices/.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=2)
    except InvalidToken:
        typer.secho(
            "Failed to decrypt VoiceDNA file. Password is incorrect or file is not a valid .voicedna.enc artifact.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=2)


@app.command("birth")
def birth(
    imprint: str = typer.Option(..., help="Imprint audio description"),
    voice_name: str = typer.Option(..., prompt=True, help="Human-friendly voice name"),
    user: str = typer.Option("", help="User/identity name (defaults to voice name slug)"),
    password: str = typer.Option(..., prompt=True, hide_input=True, confirmation_prompt=True),
    out: str = typer.Option("", help="Output file name (still stored under voices/)"),
):
    resolved_user = user or _slugify(voice_name)
    output_path = _build_voice_path(voice_name=voice_name, out=out or None)

    dna = VoiceDNA.create_new(imprint, resolved_user)
    dna.save_encrypted(password=password, filepath=str(output_path))
    typer.echo(f"Created VoiceDNA: {dna.get_recognition_id()}")
    typer.echo(f"Saved encrypted file: {output_path}")


@app.command("speak")
def speak(
    text: str = typer.Option(..., help="Text to synthesize (metadata for processing context)"),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    dna_path: str = typer.Option("myai.voicedna.enc", help="Encrypted VoiceDNA path"),
    base_model: str = typer.Option("elevenlabs", help="Target TTS base model"),
):
    dna = _load_encrypted_or_exit(password=password, dna_path=dna_path)
    processor = VoiceDNAProcessor()

    prompt = dna.generate_tts_prompt(base_model)
    processed = processor.process(
        b"RAW_TTS_AUDIO_BYTES",
        dna,
        {"text": text, "base_model": base_model, "audio_format": "wav"},
    )

    typer.echo(json.dumps(prompt, indent=2))
    typer.echo(f"Processed bytes: {len(processed)}")
    typer.echo(json.dumps(processor.get_last_report(), indent=2))


@app.command("evolve")
def evolve(
    days: int = typer.Option(1, min=1, help="Days of evolution to apply"),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    dna_path: str = typer.Option("myai.voicedna.enc", help="Encrypted VoiceDNA path"),
):
    dna = _load_encrypted_or_exit(password=password, dna_path=dna_path)
    dna.evolve(days_passed=days)
    dna.save_encrypted(password=password, filepath=dna_path)

    typer.echo(f"Updated age: {dna.get_current_age():.2f}")
    typer.echo(f"Updated imprint_strength: {dna.imprint_strength:.3f}")


@app.command("verify-password")
def verify_password(
    password: str = typer.Option(..., prompt=True, hide_input=True),
    dna_path: str = typer.Option("myai.voicedna.enc", help="Encrypted VoiceDNA path"),
):
    resolved_path = _resolve_dna_path(dna_path)
    dna = _load_encrypted_or_exit(password=password, dna_path=resolved_path)
    typer.secho("Password verification successful.", fg=typer.colors.GREEN)
    typer.echo(f"VoiceDNA: {dna.get_recognition_id()}")
    typer.echo(f"Path: {resolved_path}")


if __name__ == "__main__":
    app()
