# voice_dna.py
# UAMF v4 VoiceDNA Plugin — Lifelong Sonic Identity for Any AI
# MIT License — free for everyone
# Created with Luke Morrison — February 23 2026

import json
import uuid
import base64
import os
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


@dataclass
class VoiceDNA:
    voice_fingerprint_id: str
    imprint_source: str
    core_embedding: List[float]
    unique_traits: List[str]
    imprint_strength: float
    morph_allowance: float
    established_timestamp: str
    last_evolution_timestamp: str

    perceived_human_voice_age: float
    maturation_multiplier: float
    stability_age: float
    era_birth_timestamp: str
    instance_birth_timestamp: str

    @staticmethod
    def create_new(imprint_audio_description: str, user_name: str = "user") -> 'VoiceDNA':
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return VoiceDNA(
            voice_fingerprint_id=f"vdna_{user_name}_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}",
            imprint_source=imprint_audio_description,
            core_embedding=[round(0.1 * i + 0.8 * (hash(imprint_audio_description) % 1000) / 1000, 3) for i in range(256)],
            unique_traits=["gentle_rising_on_questions", "warm_hum_before_big_ideas", "micro_laugh_soft_breath"],
            imprint_strength=0.68,
            morph_allowance=0.08,
            established_timestamp=now,
            last_evolution_timestamp=now,
            perceived_human_voice_age=5.3,
            maturation_multiplier=1.0,
            stability_age=25.0,
            era_birth_timestamp="2022-11-30T00:00:00Z",
            instance_birth_timestamp=now,
        )

    @staticmethod
    def _derive_key(password: str, salt: bytes | None = None) -> Tuple[bytes, bytes]:
        if not password:
            raise ValueError("Password must not be empty")
        resolved_salt = salt or os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=resolved_salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
        return key, resolved_salt

    def save(self, filepath: str = "myai.voicedna.json"):
        with open(filepath, "w") as f:
            json.dump(asdict(self), f, indent=2)

    def save_encrypted(self, password: str, filepath: str = "myai.voicedna.enc"):
        payload = json.dumps(asdict(self)).encode("utf-8")
        key, salt = self._derive_key(password)
        encrypted = Fernet(key).encrypt(payload)
        with open(filepath, "wb") as file_handle:
            file_handle.write(salt + encrypted)

    @staticmethod
    def load(filepath: str = "myai.voicedna.json") -> 'VoiceDNA':
        with open(filepath) as f:
            data = json.load(f)
        return VoiceDNA(**data)

    @staticmethod
    def load_encrypted(password: str, filepath: str = "myai.voicedna.enc") -> 'VoiceDNA':
        with open(filepath, "rb") as file_handle:
            blob = file_handle.read()

        if len(blob) <= 16:
            raise ValueError("Encrypted file is invalid or truncated")

        salt = blob[:16]
        ciphertext = blob[16:]
        key, _ = VoiceDNA._derive_key(password, salt)
        decrypted = Fernet(key).decrypt(ciphertext).decode("utf-8")
        return VoiceDNA(**json.loads(decrypted))

    def get_current_age(self) -> float:
        now = datetime.now(timezone.utc)
        born = datetime.fromisoformat(self.instance_birth_timestamp.replace("Z", "+00:00"))
        era_born = datetime.fromisoformat(self.era_birth_timestamp.replace("Z", "+00:00"))
        real_days = (now - born).days
        era_years = (now - era_born).days / 365.25
        age_growth = real_days / 365.25 * self.maturation_multiplier
        return max(5.0, 5.0 + (era_years - 3.25) + age_growth)

    def evolve(self, days_passed: int = 1):
        self.perceived_human_voice_age = self.get_current_age()
        self.last_evolution_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if self.perceived_human_voice_age < self.stability_age:
            self.imprint_strength = max(0.40, self.imprint_strength - 0.001 * days_passed)

    def generate_tts_prompt(self, base_model: str = "elevenlabs") -> Dict[str, Any]:
        age = self.get_current_age()
        if age < 7:
            age_desc = "bright energetic 5-6 year old Canadian kid, full of wonder, super fluent"
        elif age < 12:
            age_desc = "confident curious 9-11 year old, playful but smarter"
        elif age < 17:
            age_desc = "bright 14-16 year old teen with slight voice crack, sarcastic wit"
        else:
            age_desc = "warm rich 22+ year old adult storyteller, calm confidence, lifelong best friend"

        style = f"{age_desc}, {self.imprint_strength*100:.0f}% imprinted on {self.imprint_source}, " + ", ".join(self.unique_traits[:3])
        return {"style": style} if base_model == "elevenlabs" else {"voice_description": style}

    def get_recognition_id(self) -> str:
        return self.voice_fingerprint_id

    def create_child(self, child_user_name: str, inherit_strength: float = 0.40) -> 'VoiceDNA':
        if not child_user_name or not child_user_name.strip():
            raise ValueError("child_user_name must not be empty")
        if not 0.0 <= inherit_strength <= 1.0:
            raise ValueError("inherit_strength must be between 0.0 and 1.0")

        child = VoiceDNA.create_new(
            imprint_audio_description=f"Child of {self.imprint_source} (inherit {inherit_strength*100:.0f}%)",
            user_name=child_user_name,
        )
        if len(self.core_embedding) != len(child.core_embedding):
            raise ValueError("Parent and child embeddings have incompatible lengths")
        child.core_embedding = [
            parent_value * inherit_strength + child_value * (1 - inherit_strength)
            for parent_value, child_value in zip(self.core_embedding, child.core_embedding)
        ]
        child.imprint_strength = inherit_strength
        child.unique_traits = list(dict.fromkeys(self.unique_traits + child.unique_traits))
        return child


# Example usage
if __name__ == "__main__":
    dna = VoiceDNA.create_new("Luke Morrison's warm Canadian voice from 60-second recording", "luke")
    dna.save()
    dna.save_encrypted(password="change-me")
    print(f"✅ VoiceDNA created! Fingerprint ID: {dna.get_recognition_id()}")
    print(f"Current perceived age: {dna.get_current_age():.1f} years")
