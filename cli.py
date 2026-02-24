import json

import typer
from cryptography.fernet import InvalidToken

from voice_dna import VoiceDNA
from voicedna import VoiceDNAProcessor


app = typer.Typer(help="VoiceDNA command line interface")


def _load_encrypted_or_exit(password: str, dna_path: str) -> VoiceDNA:
    try:
        return VoiceDNA.load_encrypted(password=password, filepath=dna_path)
    except FileNotFoundError:
        typer.secho(
            f"Encrypted VoiceDNA file not found: {dna_path}\n"
            "Tip: pass the correct path with --dna-path (for example: examples/myai.voicedna.enc).",
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
    user: str = typer.Option("user", help="User/identity name"),
    password: str = typer.Option(..., prompt=True, hide_input=True, confirmation_prompt=True),
    out: str = typer.Option("myai.voicedna.enc", help="Output encrypted VoiceDNA file path"),
):
    dna = VoiceDNA.create_new(imprint, user)
    dna.save_encrypted(password=password, filepath=out)
    typer.echo(f"Created VoiceDNA: {dna.get_recognition_id()}")
    typer.echo(f"Saved encrypted file: {out}")


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


if __name__ == "__main__":
    app()
