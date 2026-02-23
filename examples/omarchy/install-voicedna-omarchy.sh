#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OMARCHY_DIR="$ROOT_DIR/examples/omarchy"

SPEECHD_DIR="$HOME/.config/speech-dispatcher/modules"
LOCAL_BIN_DIR="$HOME/.local/bin"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
VOICEDNA_CONFIG_DIR="$HOME/.config/voicedna"
DAEMON_ENV_FILE="$VOICEDNA_CONFIG_DIR/daemon.env"

mkdir -p "$SPEECHD_DIR" "$LOCAL_BIN_DIR" "$SYSTEMD_USER_DIR" "$VOICEDNA_CONFIG_DIR"

echo "Installing/updating voicedna editable package..."
python -m pip install -e "$ROOT_DIR"

echo "Copying speech-dispatcher VoiceDNA module config..."
cp "$OMARCHY_DIR/speech-dispatcher-voicedna.conf" "$SPEECHD_DIR/voicedna.conf"

echo "Installing VoiceDNA PipeWire filter shim..."
cp "$OMARCHY_DIR/voicedna-pipewire-filter.py" "$LOCAL_BIN_DIR/voicedna-pipewire-filter.py"
chmod +x "$LOCAL_BIN_DIR/voicedna-pipewire-filter.py"

echo "Installing VoiceDNA OS daemon executable..."
cp "$OMARCHY_DIR/voicedna-os-daemon.py" "$LOCAL_BIN_DIR/voicedna-os-daemon.py"
chmod +x "$LOCAL_BIN_DIR/voicedna-os-daemon.py"

echo "Installing systemd user service..."
cp "$OMARCHY_DIR/voicedna-os-daemon.service" "$SYSTEMD_USER_DIR/voicedna-os-daemon.service"

if [[ ! -f "$DAEMON_ENV_FILE" ]]; then
	cat > "$DAEMON_ENV_FILE" <<EOF
VOICEDNA_ENC_PATH=$HOME/myai.voicedna.enc
VOICEDNA_PASSWORD=${VOICEDNA_PASSWORD:-}
VOICEDNA_DAEMON_INTERVAL_SECONDS=120
VOICEDNA_DAEMON_ANNOUNCE=0
EOF
	chmod 600 "$DAEMON_ENV_FILE"
	echo "Created daemon env file: $DAEMON_ENV_FILE"
fi

if [[ -n "${VOICEDNA_PASSWORD:-}" ]]; then
	sed -i "s#^VOICEDNA_PASSWORD=.*#VOICEDNA_PASSWORD=${VOICEDNA_PASSWORD}#" "$DAEMON_ENV_FILE"
	chmod 600 "$DAEMON_ENV_FILE"
fi

echo "Restarting user audio/speech services (best effort)..."
systemctl --user daemon-reload || true
systemctl --user enable --now voicedna-os-daemon.service || true
systemctl --user restart speech-dispatcher.service || true
systemctl --user restart wireplumber.service || true
systemctl --user restart pipewire.service || true

echo
echo "Your Omarchy desktop now speaks with your lifelong VoiceDNA voice!"
echo "Quick test: spd-say 'Hello Luke, your desktop voice is now growing with you.'"
echo "Daemon status: systemctl --user status voicedna-os-daemon.service"
