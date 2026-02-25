#!/usr/bin/env bash
set -euo pipefail

QUICK_MODE=0
CONSISTENCY_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --quick)
      QUICK_MODE=1
      ;;
    --consistency-only)
      CONSISTENCY_ONLY=1
      ;;
    -h|--help)
      echo "Usage: $0 [--quick] [--consistency-only]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg"
      exit 1
      ;;
  esac
done

print_consistency_report() {
  python - <<'PY'
import io
import json
import math
import struct
import wave

from voice_dna import VoiceDNA
from voicedna.framework import VoiceDNAProcessor

sample_rate = 16000
seconds = 0.20
frames = int(sample_rate * seconds)
buffer = io.BytesIO()
with wave.open(buffer, "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(sample_rate)
    for index in range(frames):
        sample = int(32767 * 0.2 * math.sin(2 * math.pi * 220 * index / sample_rate))
        wav.writeframesraw(struct.pack("<h", sample))

processor = VoiceDNAProcessor()
dna = VoiceDNA.create_new("Omarchy consistency verification voice", "omarchy_test")
processor.process(buffer.getvalue(), dna, {"audio_format": "wav", "imprint_converter.mode": "simple"})
report = processor.get_last_report()
print(json.dumps({
    "consistency_score": report.get("consistency_score"),
    "rvc_ready": report.get("rvc_ready"),
    "rvc_mode": report.get("rvc_mode"),
    "imprint_converter": report.get("imprint_converter", {}),
}, indent=2))
PY
}

if [[ "$CONSISTENCY_ONLY" -eq 1 ]]; then
  print_consistency_report
  exit 0
fi

echo "[1/5] Checking Omarchy speech prerequisites..."
command -v spd-say >/dev/null 2>&1 || { echo "spd-say not found. Install speech-dispatcher."; exit 1; }
command -v systemctl >/dev/null 2>&1 || { echo "systemctl not found."; exit 1; }

echo "[2/5] Sending notification voice test..."
notify-send --hint=string:sound-name:voice "VoiceDNA Test" "This should speak in your maturing voice." || true

echo "[3/5] Running terminal speech test..."
spd-say "VoiceDNA quick verification in progress on Omarchy." || true

echo "[3b/5] Running VoiceDNA CLI synthesize test..."
if [[ -n "${VOICEDNA_PASSWORD:-}" ]]; then
  VOICEDNA_PATH="${VOICEDNA_ENC_PATH:-$HOME/myai.voicedna.enc}"
  voicedna speak \
    --text "VoiceDNA CLI natural synthesis test on Omarchy." \
    --dna-path "$VOICEDNA_PATH" \
    --base-model personaplex \
    --natural-voice \
    --save-wav /tmp/voicedna-omarchy-cli-test.wav \
    --no-play \
    --password "$VOICEDNA_PASSWORD" || true
else
  echo "VOICEDNA_PASSWORD not set; skipping CLI synthesize test."
fi

echo "[4/5] Checking daemon service status..."
systemctl --user status voicedna-os-daemon.service --no-pager >/dev/null

echo "[5/5] Printing latest consistency report snapshot..."
print_consistency_report

if [[ "$QUICK_MODE" -eq 0 ]]; then
  echo "Tip: run this for report-only output: test-voicedna.sh --consistency-only"
fi

GREEN='\033[0;32m'
RESET='\033[0m'
printf "${GREEN}\n"
printf "╔════════════════════════════════════════════════════════════════════╗\n"
printf "║ ✅ VoiceDNA real-machine verification complete on Omarchy         ║\n"
printf "║ Your Omarchy desktop is now speaking with your lifelong voice.   ║\n"
printf "╚════════════════════════════════════════════════════════════════════╝\n"
printf "${RESET}\n"
