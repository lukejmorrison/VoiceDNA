#!/usr/bin/env bash
set -euo pipefail

DNA_PATH="voices/eddy42.voicedna.enc"
PASSWORD="${VOICEDNA_PASSWORD:-}"
SKIP_INSTALL=0

usage() {
  cat <<'EOF'
Usage: setup-piper-natural.sh [--dna-path PATH] [--password PASS] [--skip-install]

One-command Piper setup + VoiceDNA natural test:
1) Installs Piper packages if needed
2) Detects Piper .onnx model path
3) Writes VOICEDNA_PIPER_MODEL into ~/.config/voicedna/daemon.env
4) Restarts voicedna-os-daemon
5) Runs voicedna test-natural --show-backend

Options:
  --dna-path PATH     Encrypted VoiceDNA artifact path/name (default: voices/eddy42.voicedna.enc)
  --password PASS     Password passed directly to voicedna test-natural
  --skip-install      Skip package install step (assume Piper is already installed)
  -h, --help          Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dna-path)
      DNA_PATH="$2"
      shift 2
      ;;
    --password)
      PASSWORD="$2"
      shift 2
      ;;
    --skip-install)
      SKIP_INSTALL=1
      shift
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

ensure_piper_installed() {
  if command -v piper >/dev/null 2>&1; then
    echo "Piper binary already installed."
    return
  fi

  if [[ "$SKIP_INSTALL" -eq 1 ]]; then
    echo "--skip-install set and piper binary not found."
    echo "Install Piper first, then rerun without --skip-install or provide manual model path in daemon.env."
    exit 1
  fi

  if ! command -v yay >/dev/null 2>&1; then
    echo "yay not found. Install yay or install Piper manually."
    exit 1
  fi

  local clean_path=""
  local path_parts=()
  local filtered_parts=()
  local part
  IFS=':' read -r -a path_parts <<< "${PATH}"
  for part in "${path_parts[@]}"; do
    [[ -z "$part" ]] && continue
    if [[ -n "${VIRTUAL_ENV:-}" && "$part" == "${VIRTUAL_ENV}/bin" ]]; then
      continue
    fi
    if [[ "$part" == */.venv/bin ]]; then
      continue
    fi
    if [[ "$part" == *"/miniconda/bin" || "$part" == *"/anaconda/bin" || "$part" == *"/conda/bin" ]]; then
      continue
    fi
    filtered_parts+=("$part")
  done
  if [[ ${#filtered_parts[@]} -eq 0 ]]; then
    clean_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
  else
    clean_path="${filtered_parts[0]}"
    for part in "${filtered_parts[@]:1}"; do
      clean_path+=":${part}"
    done
  fi

  echo "Installing Piper packages with yay..."
  env -u VIRTUAL_ENV -u PYTHONPATH -u PYTHONHOME -u PIP_REQUIRE_VIRTUALENV -u CONDA_PREFIX -u PYTHON -u MAKEPKG_PYTHON \
    PATH="$clean_path" \
    yay -S --needed --noconfirm --answerclean None --answerdiff None --answeredit None --noremovemake piper-tts piper-voices-en-us || {
      echo
      echo "Piper install failed. This often happens when yay/makepkg inherits a project venv Python."
      echo "Try again from a clean shell with no active venv, then rerun this script with --skip-install."
      echo "Manual retry command: env -u VIRTUAL_ENV -u PYTHONPATH -u PYTHONHOME yay -S --needed piper-tts piper-voices-en-us"
      exit 1
    }

  if ! command -v piper >/dev/null 2>&1; then
    echo "piper binary still not found after install."
    echo "Try: yay -S piper-tts-bin piper-voices-en-us"
    exit 1
  fi
}

find_model_path() {
  local model_path
  model_path="$(find /usr/share -type f -name '*.onnx' 2>/dev/null | grep -i piper | head -n1 || true)"
  if [[ -z "$model_path" ]]; then
    model_path="$(find "$HOME" -type f -name '*.onnx' 2>/dev/null | grep -i piper | head -n1 || true)"
  fi

  if [[ -z "$model_path" ]]; then
    echo "Could not find a Piper .onnx model file."
    echo "Install piper voice package and rerun, or set VOICEDNA_PIPER_MODEL manually in ~/.config/voicedna/daemon.env"
    exit 1
  fi

  echo "$model_path"
}

write_daemon_env_value() {
  local key="$1"
  local value="$2"
  local env_file="$HOME/.config/voicedna/daemon.env"

  mkdir -p "$(dirname "$env_file")"
  touch "$env_file"

  if grep -q "^${key}=" "$env_file"; then
    sed -i "s#^${key}=.*#${key}=${value}#" "$env_file"
  else
    echo "${key}=${value}" >> "$env_file"
  fi
}

ensure_piper_installed

MODEL_PATH="$(find_model_path)"
echo "Detected Piper model: $MODEL_PATH"

write_daemon_env_value "VOICEDNA_PIPER_MODEL" "$MODEL_PATH"
write_daemon_env_value "VOICEDNA_TTS_BACKEND" "auto"

echo "Updated ~/.config/voicedna/daemon.env"
echo "Restarting voicedna-os-daemon..."
systemctl --user restart voicedna-os-daemon

echo "Running natural backend test..."
if [[ -n "$PASSWORD" ]]; then
  voicedna test-natural --dna-path "$DNA_PATH" --password "$PASSWORD" --show-backend
else
  voicedna test-natural --dna-path "$DNA_PATH" --show-backend
fi

echo
echo "Done. If backend still shows Simple, check piper runtime errors and model compatibility."