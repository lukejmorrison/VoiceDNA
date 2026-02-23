"""OpenClaw phone call skill example with voip.ms primary and Twilio fallback.

Flow:
1) Generate text response.
2) Render TTS bytes from your provider.
3) Run bytes through VoiceDNA (`voicedna_tts_hook.process_tts_output`).
4) Trigger outbound call via voip.ms bridge (or Twilio fallback).
"""

from __future__ import annotations

import base64
import logging
import os
from typing import Any

import requests

from . import voicedna_tts_hook


logger = logging.getLogger("voicedna.openclaw.phone")


def generate_bot_text(user_prompt: str) -> str:
    return f"Here is your VoiceDNA call: {user_prompt}"


def synthesize_raw_tts_bytes(text: str) -> bytes:
    """Replace with your OpenClaw TTS provider output (raw bytes)."""
    return text.encode("utf-8")


def call_via_voipms_bridge(phone_number: str, audio_bytes: bytes) -> dict[str, Any]:
    """Call through your own bridge service that speaks SIP to voip.ms.

    voip.ms setup notes:
    - Create a voip.ms sub-account dedicated to your bot.
    - Capture `VOIPMS_SUB_ACCOUNT` (username), `VOIPMS_PASSWORD`, and `VOIPMS_SERVER` (example: atlanta2.voip.ms).
    - Configure your SIP bridge to register with those credentials.
    """
    bridge_url = os.getenv("CALL_BRIDGE_URL", "http://127.0.0.1:8099/outbound-call")
    payload = {
        "provider": "voipms",
        "to": phone_number,
        "audio_b64": base64.b64encode(audio_bytes).decode("ascii"),
        "voipms": {
            "username": os.getenv("VOIPMS_SUB_ACCOUNT"),
            "password": os.getenv("VOIPMS_PASSWORD"),
            "server": os.getenv("VOIPMS_SERVER", "atlanta2.voip.ms"),
        },
    }

    if os.getenv("DRY_RUN", "0") == "1":
        logger.info("DRY_RUN enabled; skipping voip.ms bridge POST")
        return {"ok": True, "dry_run": True, "provider": "voipms", "to": phone_number}

    response = requests.post(bridge_url, json=payload, timeout=20)
    response.raise_for_status()
    return response.json() if response.content else {"ok": True, "provider": "voipms"}


def call_via_twilio(phone_number: str, audio_bytes: bytes) -> dict[str, Any]:
    """Fallback: upload audio to a reachable URL and play via Twilio TwiML."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")
    media_url = os.getenv("TWILIO_MEDIA_URL")

    if not all([account_sid, auth_token, from_number, media_url]):
        raise RuntimeError("Twilio fallback missing env vars (SID, token, from number, media URL)")

    if os.getenv("DRY_RUN", "0") == "1":
        logger.info("DRY_RUN enabled; skipping Twilio call")
        return {"ok": True, "dry_run": True, "provider": "twilio", "to": phone_number}

    twiml = f"<Response><Play>{media_url}</Play></Response>"
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"
    response = requests.post(
        url,
        data={"To": phone_number, "From": from_number, "Twiml": twiml},
        auth=(account_sid, auth_token),
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def make_growing_voice_call(phone_number: str, prompt: str) -> dict[str, Any]:
    text = generate_bot_text(prompt)
    raw_audio = synthesize_raw_tts_bytes(text)
    processed_audio = voicedna_tts_hook.process_tts_output(raw_audio, text=text, provider_name="openclaw")

    print("Ringing you now with your maturing AI voice!")

    provider = os.getenv("PHONE_PROVIDER", "voipms").lower()
    if provider == "twilio":
        return call_via_twilio(phone_number, processed_audio)

    try:
        return call_via_voipms_bridge(phone_number, processed_audio)
    except Exception as error:
        logger.warning("voip.ms call failed (%s), trying Twilio fallback", error)
        return call_via_twilio(phone_number, processed_audio)


# Optional OpenClaw decorator form:
# from openclaw import skill
#
# @skill(name="voicedna_call_me")
# def voicedna_call_me(phone_number: str, prompt: str) -> dict[str, Any]:
#     return make_growing_voice_call(phone_number, prompt)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    os.environ.setdefault("DRY_RUN", "1")
    result = make_growing_voice_call("+15551234567", "tell me a joke in your growing voice")
    print(result)
