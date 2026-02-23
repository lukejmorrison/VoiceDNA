#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OMARCHY_DIR="$ROOT_DIR/examples/omarchy"

SPEECHD_DIR="$HOME/.config/speech-dispatcher/modules"
LOCAL_BIN_DIR="$HOME/.local/bin"

mkdir -p "$SPEECHD_DIR" "$LOCAL_BIN_DIR"

echo "Installing/updating voicedna editable package..."
python -m pip install -e "$ROOT_DIR"

echo "Copying speech-dispatcher VoiceDNA module config..."
cp "$OMARCHY_DIR/speech-dispatcher-voicedna.conf" "$SPEECHD_DIR/voicedna.conf"

echo "Installing VoiceDNA PipeWire filter shim..."
cp "$OMARCHY_DIR/voicedna-pipewire-filter.py" "$LOCAL_BIN_DIR/voicedna-pipewire-filter.py"
chmod +x "$LOCAL_BIN_DIR/voicedna-pipewire-filter.py"

echo "Restarting user audio/speech services (best effort)..."
systemctl --user daemon-reload || true
systemctl --user restart speech-dispatcher.service || true
systemctl --user restart wireplumber.service || true
systemctl --user restart pipewire.service || true

echo
echo "Your Omarchy desktop now speaks with your lifelong VoiceDNA voice!"
echo "Quick test: spd-say 'Hello Luke, your desktop voice is now growing with you.'"
