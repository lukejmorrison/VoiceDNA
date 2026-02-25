import json
import re
from pathlib import Path

import typer
from cryptography.fernet import InvalidToken

from voice_dna import VoiceDNA
from voicedna.synthesis import (
    detect_natural_backend_decision,
    inspect_natural_backend_health,
    is_omarchy_environment,
    play_wav_bytes,
    synthesize_and_process,
)


app = typer.Typer(help="VoiceDNA command line interface")
VOICES_DIR = Path("voices")


def _color_for_status(color: str | None) -> typer.colors:
    if color == "green":
        return typer.colors.GREEN
    if color == "yellow":
        return typer.colors.YELLOW
    return typer.colors.CYAN


def _backend_label(resolved_backend: str) -> str:
    if resolved_backend == "personaplex":
        return "PersonaPlex (GPU)"
    if resolved_backend == "piper":
        return "Piper (Fallback)"
    if resolved_backend == "simple":
        return "Simple (Local)"
    return resolved_backend


def _print_prominent_backend_status(status_message: str, color: str | None) -> None:
    bar = "=" * 84
    terminal_color = _color_for_status(color)
    typer.secho(bar, fg=terminal_color)
    typer.secho(f"NATURAL BACKEND DECISION: {status_message}", fg=terminal_color, bold=True)
    typer.secho(bar, fg=terminal_color)


def _print_backend_banner(report: dict, resolved_backend: str) -> None:
    detected_vram_gb = report.get("detected_vram_gb")
    consistency_score = report.get("consistency_score")

    vram_text = f"{float(detected_vram_gb):.1f} GB" if isinstance(detected_vram_gb, (int, float)) else "N/A"
    consistency_text = (
        f"{float(consistency_score):.2f}" if isinstance(consistency_score, (int, float)) else "N/A"
    )
    banner_text = f"BACKEND: {_backend_label(resolved_backend)} | VRAM: {vram_text} | Consistency: {consistency_text}"

    natural_color = report.get("natural_backend_color")
    terminal_color = _color_for_status(natural_color)
    border = "#" * max(92, len(banner_text) + 8)
    typer.secho(border, fg=terminal_color)


def _print_doctor_summary(health: dict) -> None:
    bar = "-" * 84
    typer.secho(bar, fg=typer.colors.CYAN)
    typer.secho("NATURAL VOICE DOCTOR SUMMARY", fg=typer.colors.CYAN, bold=True)
    typer.secho(bar, fg=typer.colors.CYAN)
    typer.echo(f"Detected VRAM: {health.get('detected_vram', 'N/A')}")
    typer.echo(f"Natural decision: {health.get('decision')}")
    typer.echo(f"PersonaPlex runtime: {health.get('personaplex')}")
    typer.echo(f"Piper runtime: {health.get('piper')}")
    typer.echo(f"Recommended backend now: {health.get('recommended_backend')}")
    piper_model = health.get("piper_model")
    if piper_model:
        typer.echo(f"Piper model: {piper_model}")


def _print_test_summary(report: dict, resolved_backend: str) -> None:
    bar = "-" * 84
    typer.secho(bar, fg=typer.colors.GREEN)
    typer.secho("NATURAL TEST RESULT", fg=typer.colors.GREEN, bold=True)
    typer.secho(bar, fg=typer.colors.GREEN)
    typer.echo(f"Final backend: {_backend_label(resolved_backend)}")
    status = report.get("natural_backend_status")
    if isinstance(status, str) and status:
        typer.echo(f"Status: {status}")
    recommendation = report.get("natural_backend_recommendation")
    if isinstance(recommendation, str) and recommendation:
        typer.secho(f"Recommendation: {recommendation}", fg=typer.colors.YELLOW)
    piper_model = report.get("piper_model_path")
    if isinstance(piper_model, str) and piper_model:
        typer.echo(f"Piper model used: {piper_model}")
    typer.secho(f"### {banner_text} ###", fg=terminal_color, bold=True)
    typer.secho(border, fg=terminal_color)


def _run_speak(
    text: str,
    password: str,
    dna_path: str,
    base_model: str,
    natural_voice: bool,
    test_natural: bool,
    show_backend: bool,
    low_vram: bool,
    save_wav: str,
    play_audio: bool,
) -> None:
    dna = _load_encrypted_or_exit(password=password, dna_path=dna_path)

    if not text.strip():
        if test_natural:
            text = "Hello Luke, this is your natural VoiceDNA test voice on Omarchy."
        else:
            typer.secho("--text is required unless --test-natural is enabled.", fg=typer.colors.RED)
            raise typer.Exit(code=2)

    resolved_natural_voice = natural_voice or is_omarchy_environment() or test_natural
    resolved_backend = base_model

    if test_natural:
        resolved_backend = "auto"
        play_audio = True
        typer.secho("Loading natural voice...", fg=typer.colors.CYAN)
        decision = detect_natural_backend_decision(force_low_vram=low_vram)
        _print_prominent_backend_status(decision.status_message, decision.color)
        if decision.recommendation:
            typer.secho(decision.recommendation, fg=typer.colors.YELLOW)

    typer.echo(
        "Generating with PersonaPlex natural TTS..."
        if resolved_backend in {"auto", "personaplex"} and resolved_natural_voice
        else f"Generating with backend: {resolved_backend}"
    )

    try:
        processed, report, resolved_backend = synthesize_and_process(
            text=text,
            dna=dna,
            backend=resolved_backend,
            natural_voice=resolved_natural_voice,
            low_vram=low_vram,
        )
    except Exception as error:
        typer.secho(f"Synthesis failed: {error}", fg=typer.colors.RED)
        raise typer.Exit(code=2)

    natural_status = report.get("natural_backend_status")
    if isinstance(natural_status, str):
        _print_prominent_backend_status(natural_status, report.get("natural_backend_color"))

    recommendation = report.get("natural_backend_recommendation")
    if isinstance(recommendation, str) and recommendation:
        typer.secho(recommendation, fg=typer.colors.YELLOW)

    if show_backend:
        _print_backend_banner(report, resolved_backend)

    if test_natural:
        _print_test_summary(report, resolved_backend)

    if save_wav:
        save_path = Path(save_wav)
        if save_path.suffix.lower() != ".wav":
            save_path = save_path.with_suffix(".wav")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(processed)
        typer.echo(f"Saved WAV: {save_path}")

    if play_audio:
        try:
            if test_natural:
                typer.secho("Success! Playing now...", fg=typer.colors.GREEN)
            playback_backend = play_wav_bytes(processed)
            typer.echo(f"Playback backend: {playback_backend}")
        except Exception as error:
            typer.secho(f"Audio playback skipped: {error}", fg=typer.colors.YELLOW)

    typer.echo(json.dumps(dna.generate_tts_prompt(resolved_backend), indent=2))
    typer.echo(f"Processed bytes: {len(processed)}")
    typer.echo(json.dumps(report, indent=2))


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
    text: str = typer.Option("", help="Text to synthesize (metadata for processing context)"),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    dna_path: str = typer.Option("myai.voicedna.enc", help="Encrypted VoiceDNA path"),
    base_model: str = typer.Option("auto", help="TTS backend (auto, personaplex, piper, simple, elevenlabs, xtts, cartesia)"),
    natural_voice: bool = typer.Option(False, "--natural-voice", help="Prefer natural voice backend (PersonaPlex)"),
    test_natural: bool = typer.Option(False, "--test-natural", help="One-command natural voice test with auto backend selection"),
    low_vram: bool = typer.Option(False, "--lowvram", help="Force low-VRAM 4-bit PersonaPlex mode with CPU offload"),
    show_backend: bool = typer.Option(False, "--show-backend", help="Show prominent backend banner with VRAM + consistency"),
    save_wav: str = typer.Option("", help="Optional output WAV path"),
    play_audio: bool = typer.Option(True, "--play/--no-play", help="Play generated audio after processing"),
):
    _run_speak(
        text=text,
        password=password,
        dna_path=dna_path,
        base_model=base_model,
        natural_voice=natural_voice,
        test_natural=test_natural,
        show_backend=show_backend,
        low_vram=low_vram,
        save_wav=save_wav,
        play_audio=play_audio,
    )


@app.command("test-natural")
def test_natural_command(
    text: str = typer.Option("", help="Optional test text (defaults to built-in natural voice phrase)"),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    dna_path: str = typer.Option("myai.voicedna.enc", help="Encrypted VoiceDNA path"),
    low_vram: bool = typer.Option(False, "--lowvram", help="Force low-VRAM 4-bit PersonaPlex mode with CPU offload"),
    show_backend: bool = typer.Option(True, "--show-backend/--no-show-backend", help="Show prominent backend banner"),
    save_wav: str = typer.Option("", help="Optional output WAV path"),
):
    _run_speak(
        text=text,
        password=password,
        dna_path=dna_path,
        base_model="auto",
        natural_voice=True,
        test_natural=True,
        show_backend=show_backend,
        low_vram=low_vram,
        save_wav=save_wav,
        play_audio=True,
    )


@app.command("doctor-natural")
def doctor_natural_command(
    dna_path: str = typer.Option("myai.voicedna.enc", help="Encrypted VoiceDNA path"),
    password: str = typer.Option("", help="VoiceDNA password (optional; prompts only when running test)"),
    low_vram: bool = typer.Option(False, "--lowvram", help="Force low-VRAM 4-bit PersonaPlex mode with CPU offload"),
    run_test: bool = typer.Option(False, "--run-test", help="Run natural test immediately after doctor checks"),
    show_backend: bool = typer.Option(True, "--show-backend/--no-show-backend", help="Show backend banner during auto test"),
):
    health = inspect_natural_backend_health(force_low_vram=low_vram)
    decision = health.decision
    detected_vram = (
        f"{decision.detected_vram_gb:.1f} GB" if isinstance(decision.detected_vram_gb, (int, float)) else "N/A"
    )
    summary = {
        "detected_vram": detected_vram,
        "decision": decision.status_message,
        "personaplex": health.personaplex_message,
        "piper": health.piper_message,
        "recommended_backend": health.recommended_backend,
        "piper_model": health.piper_model_path,
    }
    _print_doctor_summary(summary)

    if decision.recommendation:
        typer.secho(decision.recommendation, fg=typer.colors.YELLOW)

    should_run = run_test
    if not should_run:
        should_run = typer.confirm("Run natural voice test now?", default=True)

    if not should_run:
        typer.echo("Doctor check complete. Re-run with --run-test to launch the natural test directly.")
        raise typer.Exit(code=0)

    resolved_password = password or typer.prompt("VoiceDNA password", hide_input=True)
    _run_speak(
        text="",
        password=resolved_password,
        dna_path=dna_path,
        base_model="auto",
        natural_voice=True,
        test_natural=True,
        show_backend=show_backend,
        low_vram=low_vram,
        save_wav="",
        play_audio=True,
    )


@app.command("evolve")
def evolve(
    days: int = typer.Option(1, min=1, help="Days of evolution to apply"),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    dna_path: str = typer.Option("myai.voicedna.enc", help="Encrypted VoiceDNA path"),
):
    resolved_path = _resolve_dna_path(dna_path)
    dna = _load_encrypted_or_exit(password=password, dna_path=resolved_path)
    dna.evolve(days_passed=days)
    dna.save_encrypted(password=password, filepath=resolved_path)

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
