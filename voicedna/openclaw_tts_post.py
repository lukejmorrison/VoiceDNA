"""voicedna.openclaw_tts_post — CLI post-processor for OpenClaw TTS output.

Reads a WAV file produced by OpenClaw's TTS backend (e.g. sherpa-onnx-tts),
routes it through the VoiceDNA VoiceAdapter when VOICEDNA_OPENCLAW_PRESETS=1,
and writes the processed WAV to the output path.

If VOICEDNA_OPENCLAW_PRESETS is not set the input file is passed through
unchanged (no-op) so default OpenClaw TTS behavior is never disrupted.

Usage (CLI)
-----------
    python -m voicedna.openclaw_tts_post \\
        --input  /tmp/sherpa_out.wav \\
        --output /tmp/processed.wav \\
        --agent-id agent:dr-voss-thorne \\
        --text "Greetings."

Environment variables
---------------------
VOICEDNA_OPENCLAW_PRESETS=1            Enable per-agent VoiceDNA post-processing.
VOICEDNA_OPENCLAW_PRESETS_MAP=<json>   Override agent→preset mapping (JSON object).

This module is fully additive: importing it has no side effects.  The
caller must set VOICEDNA_OPENCLAW_PRESETS to activate.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
from pathlib import Path

from voicedna.openclaw_live_voice import render_agent_voice

logger = logging.getLogger("voicedna.openclaw_tts_post")


def post_process_wav(
    input_path: str,
    output_path: str,
    agent_id: str,
    text: str = "",
    agent_name: str | None = None,
) -> bool:
    """Post-process a TTS WAV file through VoiceDNA.

    Parameters
    ----------
    input_path:
        Path to the raw WAV produced by the upstream TTS engine.
    output_path:
        Destination for the processed WAV.
    agent_id:
        Canonical agent identifier (e.g. "agent:dr-voss-thorne").
    text:
        The text that was synthesised (used for VoiceDNA parameter selection).
    agent_name:
        Optional alias for secondary preset lookup.

    Returns
    -------
    bool
        True if VoiceDNA processing was applied; False if passed through unchanged.
    """
    if not os.environ.get("VOICEDNA_OPENCLAW_PRESETS"):
        # Opt-in not active — pass through
        if input_path != output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(input_path, output_path)
        logger.debug(
            "openclaw_tts_post: VOICEDNA_OPENCLAW_PRESETS not set — pass-through."
        )
        return False

    try:
        wav_bytes = render_agent_voice(
            text=text or "",
            agent_id=agent_id,
            agent_name=agent_name,
            output_path=output_path,
        )
        if wav_bytes:
            logger.info(
                "openclaw_tts_post: applied VoiceDNA preset for %s → %s (%d bytes)",
                agent_id,
                output_path,
                len(wav_bytes),
            )
            return True
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "openclaw_tts_post: VoiceDNA synthesis failed (%s) — falling back to pass-through.",
            exc,
        )

    # Fallback: copy input unchanged
    if input_path != output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(input_path, output_path)
    return False


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=os.environ.get("VOICEDNA_LOG_LEVEL", "WARNING"),
        format="[voicedna-tts-post] %(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        prog="python -m voicedna.openclaw_tts_post",
        description="Post-process an OpenClaw TTS WAV through VoiceDNA (opt-in).",
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        metavar="FILE",
        help="Input WAV file (raw TTS output).",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        metavar="FILE",
        help="Output WAV file (processed audio).",
    )
    parser.add_argument(
        "--agent-id",
        default="",
        metavar="ID",
        help='Canonical agent ID (e.g. "agent:dr-voss-thorne").',
    )
    parser.add_argument(
        "--agent-name",
        default=None,
        metavar="NAME",
        help="Optional agent name alias for secondary preset lookup.",
    )
    parser.add_argument(
        "--text",
        default="",
        metavar="TEXT",
        help="The original TTS text (used for VoiceDNA parameter selection).",
    )

    args = parser.parse_args(argv)

    if not Path(args.input).exists():
        print(f"[voicedna-tts-post] ERROR: Input file not found: {args.input}", file=sys.stderr)
        return 1

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    applied = post_process_wav(
        input_path=args.input,
        output_path=args.output,
        agent_id=args.agent_id,
        text=args.text,
        agent_name=args.agent_name,
    )

    if applied:
        print(f"[voicedna-tts-post] VoiceDNA applied → {args.output}")
    else:
        print(f"[voicedna-tts-post] Pass-through → {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
