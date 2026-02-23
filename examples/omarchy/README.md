# Make your Omarchy desktop speak with your growing AI voice in 5 minutes

This guide gives your whole Omarchy desktop (Arch + Hyprland) a unique, maturing VoiceDNA voice for screen reader output, desktop speech, and quick terminal speech tests.

## What you get

- PipeWire filter bridge that can process TTS audio through `VoiceDNAProcessor`
- Speech Dispatcher profile that points speech output to VoiceDNA hooks
- Optional tiny background daemon pattern for custom events/notifications
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

This script:
- installs/updates `voicedna` in your active Python environment
- copies `speech-dispatcher-voicedna.conf` into `~/.config/speech-dispatcher/modules/`
- installs `voicedna-pipewire-filter.py` into `~/.local/bin/`
- restarts user services (`speech-dispatcher`, `wireplumber`, `pipewire`)

## 3) PipeWire filter module path

The sample script (`voicedna-pipewire-filter.py`) is a practical shim:
- receives bytes from stdin (or a file)
- processes audio via `VoiceDNAProcessor`
- writes transformed bytes to stdout

Use it in your own PipeWire `filter-chain` or desktop TTS wrapper command.

## 4) Speech Dispatcher config

The included `speech-dispatcher-voicedna.conf` sets VoiceDNA as default output module behavior for desktop speech flow.

After installation, test:

```bash
spd-say "Hello Luke, your desktop voice is now growing with you."
```

## 5) Optional lightweight daemon

You can run a tiny loop that sends notifications/highlight-to-speak text through `spd-say`, while the VoiceDNA speech module is active:

```bash
while true; do
  sleep 60
  spd-say "VoiceDNA daemon heartbeat: your desktop voice is alive."
done
```

## One-command install recap

```bash
bash examples/omarchy/install-voicedna-omarchy.sh
```

When complete, you should see:

`Your Omarchy desktop now speaks with your lifelong VoiceDNA voice!`
