import base64
from typing import Dict

from voice_dna import VoiceDNA

from .base import IVoiceDNAFilter


class PromptTagFilter(IVoiceDNAFilter):
    def name(self) -> str:
        return "prompt_tag"

    def priority(self) -> int:
        return 10

    def process(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict) -> bytes:
        if not params.get("prepend_style_tag", False):
            return audio_bytes

        style = dna.generate_tts_prompt(params.get("base_model", "elevenlabs"))
        if "style" in style:
            tag_value = style["style"]
        else:
            tag_value = style.get("voice_description", "")
        prefix = f"[VoiceDNA:{dna.get_recognition_id()}::{tag_value}]\n".encode("utf-8")
        return prefix + audio_bytes


class Base64PassThroughFilter(IVoiceDNAFilter):
    def name(self) -> str:
        return "base64_passthrough"

    def priority(self) -> int:
        return 50

    def process(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict) -> bytes:
        if not params.get("round_trip_base64", False):
            return audio_bytes

        encoded = base64.b64encode(audio_bytes)
        return base64.b64decode(encoded)
