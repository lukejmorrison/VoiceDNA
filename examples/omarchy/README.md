# Make your Omarchy desktop speak with your growing AI voice in 5 minutes

## 🔬 Quick Test on Your Real Omarchy Machine (5–10 minutes)

### Prerequisites

- Omarchy (Arch + Hyprland) is installed
- PipeWire is running (`systemctl --user status pipewire`)
- `speech-dispatcher` is installed (`sudo pacman -S --needed speech-dispatcher`)

### One-liner install + test mode

```bash
bash examples/omarchy/install-voicedna-omarchy.sh --test-mode
```

### Natural voice mode (PersonaPlex, optional)

```bash
bash examples/omarchy/install-voicedna-omarchy.sh --natural-voice --test-mode
```

This enables the optional PersonaPlex backend for speech-dispatcher and daemon probe flows.
GPU acceleration is strongly recommended for real-time desktop usage.

### Step-by-step verification commands

1) Birth a fresh VoiceDNA:

```bash
voicedna birth --imprint "Luke real Omarchy machine test voice" --user luke_omarchy_test --password
```

2) Test notification voice:

```bash
notify-send --hint=string:sound-name:voice "VoiceDNA Test" "This should speak in your maturing voice"
```

3) Test terminal speech-dispatcher speak path:

```bash
spd-say "VoiceDNA terminal test. Omarchy desktop voice check."
```

3b) Test VoiceDNA CLI natural synthesis path:

```bash
voicedna speak --text "Hello from Eddy42 natural voice test." --dna-path voices/eddy42.voicedna.enc --base-model personaplex --natural-voice
```

4) Check daemon status:

```bash
systemctl --user status voicedna-os-daemon
```

5) Check consistency report (`consistency_score`):

```bash
/home/$USER/.local/bin/test-voicedna.sh --consistency-only
```

## Try it now (one sentence)

```bash
bash examples/omarchy/install-voicedna-omarchy.sh && spd-say "VoiceDNA is active. Your Omarchy desktop now speaks in your growing voice."
```

The installer enables a user daemon that runs silently in the background after login/reboot.
VoiceDNA v2.7 adds a consistency layer that continuously reinforces your core voice embedding and stamps subtle machine-recognizable identity watermarking.

This guide gives your whole Omarchy desktop (Arch + Hyprland) a unique, maturing VoiceDNA voice for screen reader output, desktop speech, and quick terminal speech tests.

## What you get

- PipeWire filter bridge that can process TTS audio through `VoiceDNAProcessor`
- Speech Dispatcher profile that points speech output to VoiceDNA hooks
- User-level systemd daemon that auto-starts after login/reboot
- One-command installer script for Omarchy users

## 1) Install VoiceDNA + speech dependencies

```bash
cd /path/to/VoiceDNA
pip install -e .
sudo pacman -S --needed speech-dispatcher pipewire wireplumber
```

## 2) Run the one-command install script

```bash
bash examples/omarchy/install-voicedna-omarchy.sh
```

Natural voice mode (optional PersonaPlex backend):

```bash
bash examples/omarchy/install-voicedna-omarchy.sh --natural-voice
```

This script:
- installs/updates `voicedna` in your active Python environment
- optionally installs PersonaPlex dependencies with `--natural-voice`
- copies `speech-dispatcher-voicedna.conf` into `~/.config/speech-dispatcher/modules/`
- installs `voicedna-pipewire-filter.py` into `~/.local/bin/`
- installs `voicedna-os-daemon.py` and enables `voicedna-os-daemon.service`
- writes `~/.config/voicedna/daemon.env` (env-based password path)
- restarts user services (`speech-dispatcher`, `wireplumber`, `pipewire`)

## 3) PipeWire filter module path

The sample script (`voicedna-pipewire-filter.py`) is a practical shim:
- receives bytes from stdin (or a file)
- processes audio via `VoiceDNAProcessor`
- writes transformed bytes to stdout

Use it in your own PipeWire `filter-chain` or desktop TTS wrapper command.

## 4) Speech Dispatcher config

The included `speech-dispatcher-voicedna.conf` sets VoiceDNA as default output module behavior for desktop speech flow.

In natural voice mode, the module invokes the PersonaPlex synth path and then runs VoiceDNA processing.

After installation, test:

```bash
spd-say "Hello Luke, your desktop voice is now growing with you."
```

## 5) Background daemon (auto-start)

The installer enables:

- `~/.config/systemd/user/voicedna-os-daemon.service`

It auto-loads encrypted VoiceDNA on login/reboot using:

1. `VOICEDNA_PASSWORD` in `~/.config/voicedna/daemon.env` (default path)
2. `keyring` secret (service=`voicedna`, user=`default`) if available

Check status:

```bash
systemctl --user status voicedna-os-daemon.service
```

View logs:

```bash
journalctl --user -u voicedna-os-daemon.service -f
```

## One-command install recap

```bash
bash examples/omarchy/install-voicedna-omarchy.sh
```

When complete, you should see:

`Your Omarchy desktop now speaks with your lifelong VoiceDNA voice!`

## Future RVC mode note

Desktop voice cloning is currently wired through the RVC-ready path. A future mode will enable direct RVC desktop conversion for richer system-wide voice timbre.

## PersonaPlex environment knobs

Edit `~/.config/voicedna/daemon.env` if needed:

- `VOICEDNA_TTS_BACKEND=personaplex`
- `VOICEDNA_PERSONAPLEX_MODEL=nvidia/personaplex-7b-v1`
- `VOICEDNA_PERSONAPLEX_DEVICE=auto`
- `VOICEDNA_PERSONAPLEX_DTYPE=auto`
