# voice_dna.py
# UAMF v4 VoiceDNA Plugin — Lifelong Sonic Identity for Any AI
# MIT License — free for everyone
# Created with Luke Morrison — February 23 2026

import json
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


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

    def save(self, filepath: str = "myai.voicedna.json"):
        with open(filepath, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @staticmethod
    def load(filepath: str = "myai.voicedna.json") -> 'VoiceDNA':
        with open(filepath) as f:
            data = json.load(f)
        return VoiceDNA(**data)

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


# Example usage
if __name__ == "__main__":
    dna = VoiceDNA.create_new("Luke Morrison's warm Canadian voice from 60-second recording", "luke")
    dna.save()
    print(f"✅ VoiceDNA created! Fingerprint ID: {dna.get_recognition_id()}")
    print(f"Current perceived age: {dna.get_current_age():.1f} years")
