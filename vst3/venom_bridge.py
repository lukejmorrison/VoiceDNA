from __future__ import annotations

from dataclasses import dataclass
import random
from pathlib import Path

from voice_dna import VoiceDNA
from voicedna import VoiceDNAProcessor


@dataclass
class VenomBridgeConfig:
    dna_path: str
    password: str


class VoiceDNAVenomBridge:
    def __init__(self, config: VenomBridgeConfig):
        self.config = config
        self.dna = VoiceDNA.load_encrypted(password=config.password, filepath=config.dna_path)
        self.processor = VoiceDNAProcessor()

    def process_pcm_bytes(
        self,
        audio_bytes: bytes,
        base_model: str = "vst3_reaper",
        *,
        force_age: float | None = None,
        imprint_strength: float | None = None,
    ) -> bytes:
        params = {
            "audio_format": "wav",
            "base_model": base_model,
            "imprint_converter.mode": "simple",
        }
        if force_age is not None:
            params["force_age"] = float(force_age)
        if imprint_strength is not None:
            self.dna.imprint_strength = max(0.0, min(1.0, float(imprint_strength)))
        return self.processor.process(audio_bytes, self.dna, params)

    def birth_child_from_parent_files(
        self,
        parent_a_path: str,
        parent_b_path: str,
        *,
        child_user_name: str,
        output_path: str,
        inherit_parent_a: float = 50.0,
        inherit_parent_b: float = 50.0,
        randomness: float = 10.0,
        password: str | None = None,
    ) -> dict:
        parent_a = VoiceDNA.create_new(parent_a_path, user_name="parent_a")
        parent_b = VoiceDNA.create_new(parent_b_path, user_name="parent_b")
        child = VoiceDNA.create_new(
            imprint_audio_description=f"Child of {Path(parent_a_path).name} + {Path(parent_b_path).name}",
            user_name=child_user_name,
        )

        total = max(0.0001, float(inherit_parent_a) + float(inherit_parent_b))
        weight_a = float(inherit_parent_a) / total
        weight_b = float(inherit_parent_b) / total
        jitter_scale = max(0.0, min(100.0, float(randomness))) / 100.0 * 0.08

        child.core_embedding = [
            max(-1.0, min(1.0, (a * weight_a) + (b * weight_b) + (random.uniform(-1.0, 1.0) * jitter_scale)))
            for a, b in zip(parent_a.core_embedding, parent_b.core_embedding)
        ]
        child.unique_traits = list(dict.fromkeys(parent_a.unique_traits + parent_b.unique_traits + child.unique_traits))
        child.imprint_strength = max(0.0, min(1.0, (weight_a + weight_b) / 2.0))

        save_password = password or self.config.password
        child.save_encrypted(password=save_password, filepath=output_path)

        return {
            "status": "ok",
            "child_id": child.get_recognition_id(),
            "output_path": output_path,
            "inherit_parent_a": float(inherit_parent_a),
            "inherit_parent_b": float(inherit_parent_b),
            "randomness": float(randomness),
        }

    def get_last_report(self) -> dict:
        return self.processor.get_last_report()
