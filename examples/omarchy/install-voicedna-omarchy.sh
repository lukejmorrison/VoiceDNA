#!/usr/bin/env bash
set -euo pipefail

TEST_MODE=0
NATURAL_VOICE_MODE=0
for arg in "$@"; do
	case "$arg" in
		--test-mode)
			TEST_MODE=1
			;;
		--natural-voice)
			NATURAL_VOICE_MODE=1
			;;
		-h|--help)
			echo "Usage: $0 [--test-mode] [--natural-voice]"
			echo "  --test-mode   Run 30-second verification after install"
			echo "  --natural-voice  Enable VRAM-aware natural voice mode (PersonaPlex/Piper)"
			exit 0
			;;
		*)
			echo "Unknown argument: $arg"
			echo "Usage: $0 [--test-mode] [--natural-voice]"
			exit 1
			;;
	esac
done

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

if [[ "$NATURAL_VOICE_MODE" -eq 1 ]]; then
	echo "Installing optional PersonaPlex runtime dependencies..."
	python -m pip install -e "$ROOT_DIR[personaplex]"
fi

echo "Copying speech-dispatcher VoiceDNA module config..."
cp "$OMARCHY_DIR/speech-dispatcher-voicedna.conf" "$SPEECHD_DIR/voicedna.conf"

if [[ "$NATURAL_VOICE_MODE" -eq 1 ]]; then
	sed -i 's/--tts-backend simple/--tts-backend auto/' "$SPEECHD_DIR/voicedna.conf"
fi

echo "Installing VoiceDNA PipeWire filter shim..."
cp "$OMARCHY_DIR/voicedna-pipewire-filter.py" "$LOCAL_BIN_DIR/voicedna-pipewire-filter.py"
chmod +x "$LOCAL_BIN_DIR/voicedna-pipewire-filter.py"

echo "Installing VoiceDNA test helper..."
cp "$OMARCHY_DIR/test-voicedna.sh" "$LOCAL_BIN_DIR/test-voicedna.sh"
chmod +x "$LOCAL_BIN_DIR/test-voicedna.sh"

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
VOICEDNA_TTS_BACKEND=auto
VOICEDNA_PERSONAPLEX_MODEL=nvidia/personaplex-7b-v1
VOICEDNA_PERSONAPLEX_DEVICE=auto
VOICEDNA_PERSONAPLEX_DTYPE=auto
VOICEDNA_MIN_PERSONAPLEX_VRAM_GB=12
VOICEDNA_PIPER_MODEL=
VOICEDNA_PIPER_EXECUTABLE=piper
VOICEDNA_PIPER_SPEAKER=
EOF
	chmod 600 "$DAEMON_ENV_FILE"
	echo "Created daemon env file: $DAEMON_ENV_FILE"
fi

if [[ -n "${VOICEDNA_PASSWORD:-}" ]]; then
	sed -i "s#^VOICEDNA_PASSWORD=.*#VOICEDNA_PASSWORD=${VOICEDNA_PASSWORD}#" "$DAEMON_ENV_FILE"
	chmod 600 "$DAEMON_ENV_FILE"
fi

if [[ "$NATURAL_VOICE_MODE" -eq 1 ]]; then
	sed -i 's#^VOICEDNA_TTS_BACKEND=.*#VOICEDNA_TTS_BACKEND=auto#' "$DAEMON_ENV_FILE" || true
	grep -q '^VOICEDNA_TTS_BACKEND=' "$DAEMON_ENV_FILE" || echo 'VOICEDNA_TTS_BACKEND=auto' >> "$DAEMON_ENV_FILE"
	chmod 600 "$DAEMON_ENV_FILE"
fi

echo "Restarting user audio/speech services (best effort)..."
systemctl --user daemon-reload || true
systemctl --user enable --now voicedna-os-daemon.service || true
systemctl --user restart speech-dispatcher.service || true
systemctl --user restart wireplumber.service || true
systemctl --user restart pipewire.service || true

if [[ "$TEST_MODE" -eq 1 ]]; then
	echo
	echo "Running 30-second VoiceDNA test sequence..."

	if [[ ! -f "$HOME/myai.voicedna.enc" ]]; then
		echo "No encrypted DNA found; creating a fresh test identity..."
		TEST_PASSWORD="${VOICEDNA_PASSWORD:-voicedna_test_mode}"
		python - <<PY
from voice_dna import VoiceDNA
dna = VoiceDNA.create_new("Luke Omarchy real-machine installer test imprint", "luke_omarchy")
dna.save_encrypted(password="${TEST_PASSWORD}", filepath="${HOME}/myai.voicedna.enc")
print("Created encrypted VoiceDNA at ${HOME}/myai.voicedna.enc")
PY

		if [[ -z "${VOICEDNA_PASSWORD:-}" ]]; then
			sed -i "s#^VOICEDNA_PASSWORD=.*#VOICEDNA_PASSWORD=${TEST_PASSWORD}#" "$DAEMON_ENV_FILE"
			chmod 600 "$DAEMON_ENV_FILE"
			echo "Set test-mode daemon password in $DAEMON_ENV_FILE"
		fi
	fi

	notify-send --hint=string:sound-name:voice "VoiceDNA Test" "Installer test-mode is active. This should speak in your maturing voice." || true
	spd-say "VoiceDNA Omarchy test mode is active. Your desktop voice is now verified." || true
	"$LOCAL_BIN_DIR/test-voicedna.sh" --quick || true
fi

echo
echo "Your Omarchy desktop now speaks with your lifelong VoiceDNA voice!"
if [[ "$NATURAL_VOICE_MODE" -eq 1 ]]; then
	echo "Natural voice mode: VRAM-aware backend enabled (PersonaPlex on high VRAM, Piper fallback on consumer GPUs)."
fi
echo "Quick test: spd-say 'Hello Luke, your desktop voice is now growing with you.'"
echo "Daemon status: systemctl --user status voicedna-os-daemon.service"
