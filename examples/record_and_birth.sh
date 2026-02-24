#!/usr/bin/env bash
set -euo pipefail

SECONDS_TO_RECORD=10
USER_NAME="${USER:-user}"
VOICE_NAME=""
OUT_PATH=""
AUDIO_PATH=""
KEEP_AUDIO=0
RECORDER="auto"
PULSE_DEVICE="default"
ALSA_DEVICE="default"
SAMPLE_RATE=16000
CHANNELS=1

usage() {
	echo "Usage: $0 [options]"
	echo
	echo "Record mic audio and immediately create encrypted VoiceDNA."
	echo
	echo "Options:"
	echo "  --seconds N         Recording length in seconds (default: 10)"
	echo "  --voice-name NAME   Human-friendly voice name (prompts if omitted)"
	echo "  --user NAME         VoiceDNA user/identity name (default: current user)"
	echo "  --out PATH          Output file name (always saved under voices/)"
	echo "  --audio-out PATH    Keep/use this WAV path for recorded audio"
	echo "  --keep-audio        Keep recorded WAV file after birth"
	echo "  --recorder NAME     auto | arecord | pw-record | ffmpeg (default: auto)"
	echo "  --pulse-device DEV  Pulse device for ffmpeg mode (default: default)"
	echo "  --alsa-device DEV   ALSA device for ffmpeg/arecord mode (default: default)"
	echo "  --sample-rate N     Recording sample rate (default: 16000)"
	echo "  --channels N        Recording channels (default: 1)"
	echo "  -h, --help          Show help"
	echo
	echo "Environment:"
	echo "  VOICEDNA_PASSWORD   Optional password (if omitted, prompt is shown securely)"
	echo "  PYTHON_BIN          Python executable (default: python3, falls back to python)"
}

while [[ $# -gt 0 ]]; do
	case "$1" in
		--seconds)
			SECONDS_TO_RECORD="$2"
			shift 2
			;;
		--user)
			USER_NAME="$2"
			shift 2
			;;
		--voice-name)
			VOICE_NAME="$2"
			shift 2
			;;
		--out)
			OUT_PATH="$2"
			shift 2
			;;
		--audio-out)
			AUDIO_PATH="$2"
			KEEP_AUDIO=1
			shift 2
			;;
		--keep-audio)
			KEEP_AUDIO=1
			shift
			;;
		--recorder)
			RECORDER="$2"
			shift 2
			;;
		--pulse-device)
			PULSE_DEVICE="$2"
			shift 2
			;;
		--alsa-device)
			ALSA_DEVICE="$2"
			shift 2
			;;
		--sample-rate)
			SAMPLE_RATE="$2"
			shift 2
			;;
		--channels)
			CHANNELS="$2"
			shift 2
			;;
		-h|--help)
			usage
			exit 0
			;;
		*)
			echo "Unknown argument: $1"
			usage
			exit 1
			;;
	esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CREATE_SCRIPT="$SCRIPT_DIR/create_from_audio.py"

if [[ ! -f "$CREATE_SCRIPT" ]]; then
	echo "Missing helper script: $CREATE_SCRIPT"
	exit 1
fi

if [[ -z "$AUDIO_PATH" ]]; then
	AUDIO_PATH="/tmp/voicedna-record-$(date +%Y%m%d-%H%M%S).wav"
fi

if [[ -z "$VOICE_NAME" ]]; then
	read -r -p "Voice name: " VOICE_NAME
fi

if [[ -z "$VOICE_NAME" ]]; then
	echo "Voice name must not be empty."
	exit 1
fi

VOICE_SLUG="$(echo "$VOICE_NAME" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/_/g; s/^_+|_+$//g; s/_+/_/g')"
if [[ -z "$VOICE_SLUG" ]]; then
	VOICE_SLUG="voice"
fi

mkdir -p voices

if [[ -n "$OUT_PATH" ]]; then
	OUT_FILE="$(basename "$OUT_PATH")"
else
	OUT_FILE="${VOICE_SLUG}.voicedna.enc"
fi

if [[ "$OUT_FILE" != *.voicedna.enc ]]; then
	OUT_FILE="${OUT_FILE}.voicedna.enc"
fi

OUT_PATH="voices/${OUT_FILE}"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
	if command -v python >/dev/null 2>&1; then
		PYTHON_BIN="python"
	else
		echo "Python executable not found. Set PYTHON_BIN or install python3."
		exit 1
	fi
fi

record_with_arecord() {
	if ! command -v arecord >/dev/null 2>&1; then
		return 1
	fi
	echo "Recording ${SECONDS_TO_RECORD}s using arecord..."
	arecord -q -D "$ALSA_DEVICE" -d "$SECONDS_TO_RECORD" -f S16_LE -r "$SAMPLE_RATE" -c "$CHANNELS" "$AUDIO_PATH"
}

record_with_pw_record() {
	if ! command -v pw-record >/dev/null 2>&1; then
		return 1
	fi
	echo "Recording ${SECONDS_TO_RECORD}s using pw-record..."
	PW_ARGS=(--rate "$SAMPLE_RATE" --channels "$CHANNELS" "$AUDIO_PATH")
	if [[ "$PULSE_DEVICE" != "default" ]]; then
		PW_ARGS=(--target "$PULSE_DEVICE" "${PW_ARGS[@]}")
	fi

	if command -v timeout >/dev/null 2>&1; then
		timeout "${SECONDS_TO_RECORD}s" pw-record "${PW_ARGS[@]}" || {
			status=$?
			if [[ "$status" -ne 124 ]]; then
				return "$status"
			fi
		}
		return 0
	fi

	pw-record "${PW_ARGS[@]}" &
	recorder_pid=$!
	sleep "$SECONDS_TO_RECORD"
	kill -INT "$recorder_pid" >/dev/null 2>&1 || true
	wait "$recorder_pid" || true
}

record_with_ffmpeg_pulse() {
	if ! command -v ffmpeg >/dev/null 2>&1; then
		return 1
	fi
	echo "Recording ${SECONDS_TO_RECORD}s using ffmpeg (pulse:${PULSE_DEVICE})..."
	ffmpeg -loglevel error -f pulse -i "$PULSE_DEVICE" -t "$SECONDS_TO_RECORD" -ac "$CHANNELS" -ar "$SAMPLE_RATE" -y "$AUDIO_PATH" || return 1
}

record_with_ffmpeg_alsa() {
	if ! command -v ffmpeg >/dev/null 2>&1; then
		return 1
	fi
	echo "Recording ${SECONDS_TO_RECORD}s using ffmpeg (alsa:${ALSA_DEVICE})..."
	ffmpeg -loglevel error -f alsa -i "$ALSA_DEVICE" -t "$SECONDS_TO_RECORD" -ac "$CHANNELS" -ar "$SAMPLE_RATE" -y "$AUDIO_PATH" || return 1
}

record_with_ffmpeg() {
	record_with_ffmpeg_pulse || record_with_ffmpeg_alsa
}

case "$RECORDER" in
	auto)
		record_with_arecord || record_with_pw_record || record_with_ffmpeg || {
			echo "No supported recorder found. Install one of: arecord (alsa-utils), pw-record (pipewire), or ffmpeg with pulse/alsa input support."
			exit 1
		}
		;;
	arecord)
		record_with_arecord || {
			echo "arecord mode requested but arecord is not available."
			exit 1
		}
		;;
	pw-record)
		record_with_pw_record || {
			echo "pw-record mode requested but pw-record is not available."
			exit 1
		}
		;;
	ffmpeg)
		record_with_ffmpeg || {
			echo "ffmpeg mode requested but compatible ffmpeg input was not available (pulse/alsa)."
			exit 1
		}
		;;
	*)
		echo "Invalid --recorder value: $RECORDER"
		exit 1
		;;
esac

if [[ ! -s "$AUDIO_PATH" ]]; then
	echo "Recording failed; audio file is empty: $AUDIO_PATH"
	exit 1
fi

echo "Creating encrypted VoiceDNA from: $AUDIO_PATH"

CREATE_CMD=("$PYTHON_BIN" "$CREATE_SCRIPT" --audio "$AUDIO_PATH" --user "$USER_NAME" --out "$OUT_PATH")
CREATE_CMD+=(--voice-name "$VOICE_NAME")

if [[ -n "${VOICEDNA_PASSWORD:-}" ]]; then
	CREATE_CMD+=(--password "$VOICEDNA_PASSWORD")
fi

"${CREATE_CMD[@]}"

if [[ "$KEEP_AUDIO" -eq 0 ]]; then
	rm -f "$AUDIO_PATH"
	echo "Removed temporary recording: $AUDIO_PATH"
else
	echo "Kept recording: $AUDIO_PATH"
fi

echo "Done. New encrypted VoiceDNA: $OUT_PATH"
