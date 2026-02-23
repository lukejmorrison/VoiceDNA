# 5-Minute OpenClaw + VoiceDNA Testing Path (new or existing deployment)

This is the fastest path to hear your bot speak with a maturing VoiceDNA voice and then call your real phone for a full conversation.

## Prerequisites

- Python 3.10+
- VoiceDNA installed (`pip install -e .` from this repo)
- An OpenClaw deployment (new or existing)
- Encrypted VoiceDNA file at `myai.voicedna.enc`

---

## New deployment (fresh install + skill)

1) Install OpenClaw:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

2) Install VoiceDNA into the same environment where OpenClaw skills run:

```bash
cd /path/to/VoiceDNA
pip install -e .
```

3) Copy these two skills into your OpenClaw skills/extensions folder:

- `examples/openclaw/voicedna_tts_hook.py`
- `examples/openclaw/voipms_phone_skill.py`

4) Restart OpenClaw so it loads the new skill files.

---

## Existing deployment (just add the hook)

1) Copy `examples/openclaw/voicedna_tts_hook.py` into your existing OpenClaw `skills/` (or `extensions/`) folder.

2) Set password env var (recommended) so there is no prompt:

```bash
export VOICEDNA_PASSWORD="your_password_here"
```

3) Restart OpenClaw.

Now any TTS raw bytes can be routed through `process_tts_output(...)` before playback/streaming.

---

## How to load the encrypted VoiceDNA file

By default, the hook loads:

- `myai.voicedna.enc`

Password resolution order:

1. `VOICEDNA_PASSWORD` environment variable
2. Runtime prompt fallback (`getpass`) in terminal

Optional override env vars:

- `VOICEDNA_ENC_PATH` (alternate encrypted file path)
- `VOICEDNA_FORCE_AGE` (example: `15` to test teen stage)

---

## How to enable the Voice Call plugin for phone calls

OpenClaw provides `@openclaw/voice-call` for outbound and multi-turn calls.

1) Enable/install the plugin in your OpenClaw instance.
2) Configure your provider credentials (`voip.ms` SIP or Twilio).
3) Keep `voipms_phone_skill.py` loaded so generated speech can pass through VoiceDNA before dialing.

If your deployment uses an internal call bridge, point `CALL_BRIDGE_URL` at that bridge and use `DRY_RUN=1` first.

---

## 3-command flow

```bash
cd /path/to/VoiceDNA
pip install -e .
python -c "import examples.openclaw.voicedna_tts_hook, examples.openclaw.voipms_phone_skill; print('OpenClaw skills import OK')"
```

---

## Example command to trigger a test call

In your OpenClaw chat/console:

> Claw, call me on my phone and tell me a joke in your growing voice

Expected console line from the skill:

`Ringing you now with your maturing AI voice!`
