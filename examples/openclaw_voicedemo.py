"""examples/openclaw_voicedemo.py — Per-agent voice demo for VoiceDNA + OpenClaw.

Produces three WAV files under examples/openclaw/output/:
  - namshub_neutral.wav
  - david_friendly.wav
  - voss_flair.wav

Run:
    cd /path/to/VoiceDNA
    python examples/openclaw_voicedemo.py

Opt-in env var:
    VOICEDNA_OPENCLAW_PRESETS=1   (not required to run the demo; presence is checked)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow running from repo root without installing
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from voicedna.openclaw_adapter import VoiceAdapter

OUTPUT_DIR = Path(__file__).parent / "openclaw" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ----- Agent → preset mapping (inline for demo; production uses env/config) -----
AGENT_PRESET_MAP = {
    "agent:namshub": "neutral",
    "agent:david-hardman": "friendly",
    "agent:dr-voss-thorne": "flair",
}

AGENT_LINES = {
    "agent:namshub": "Hello. I am Namshub, your primary orchestration agent.",
    "agent:david-hardman": "Hey there! David Hardman here — happy to help with anything you need today.",
    "agent:dr-voss-thorne": "Greetings. Dr Voss Thorne. Precision is the only acceptable standard.",
}

OUTPUT_NAMES = {
    "agent:namshub": "namshub_neutral.wav",
    "agent:david-hardman": "david_friendly.wav",
    "agent:dr-voss-thorne": "voss_flair.wav",
}


def main() -> None:
    if not os.environ.get("VOICEDNA_OPENCLAW_PRESETS"):
        print(
            "[voicedna-demo] Tip: set VOICEDNA_OPENCLAW_PRESETS=1 to signal opt-in mode in production.\n"
            "                Running demo regardless.\n"
        )

    adapter = VoiceAdapter(agent_presets=AGENT_PRESET_MAP)

    produced: list[str] = []
    for agent_id, text in AGENT_LINES.items():
        preset = adapter.select_preset(agent_id)
        out_path = OUTPUT_DIR / OUTPUT_NAMES[agent_id]
        print(f"[{agent_id}] preset={preset!r}  → {out_path}")
        adapter.synthesize(text, preset, output_path=str(out_path))
        produced.append(str(out_path))

    print("\n✓ Demo complete. Output files:")
    for p in produced:
        size = Path(p).stat().st_size
        print(f"  {p}  ({size} bytes)")


if __name__ == "__main__":
    main()
