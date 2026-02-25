#!/usr/bin/env bash
set -euo pipefail

print_free_vram() {
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=memory.free,memory.total --format=csv,noheader || true
  else
    echo "nvidia-smi not found"
  fi
}

echo "[0/4] Free VRAM before cleanup"
print_free_vram

echo "[1/4] GPU memory snapshot"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi -q -d MEMORY || true
else
  echo "nvidia-smi not found; skipping GPU query"
fi

echo "[2/4] Clearing torch CUDA cache"
python - <<'PY'
try:
    import torch
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        print("Torch CUDA cache cleared")
    else:
        print("CUDA not available in torch; skipping cache clear")
except Exception as error:
    print(f"Torch cache clear skipped: {error}")
PY

echo "[3/4] Syncing filesystem buffers"
sync || true

echo "[4/4] Dropping Linux page cache (requires root)"
if [[ "${EUID}" -eq 0 ]]; then
  echo 3 > /proc/sys/vm/drop_caches
  echo "Page cache dropped"
elif command -v sudo >/dev/null 2>&1; then
  echo "Trying with sudo..."
  echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null
  echo "Page cache drop requested via sudo"
else
  echo "No root/sudo privileges; skipping drop_caches"
fi

echo "[after] Free VRAM after cleanup"
print_free_vram

echo "VRAM/system cache clear routine complete."
