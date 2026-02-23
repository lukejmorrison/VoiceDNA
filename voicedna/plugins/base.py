from abc import ABC, abstractmethod
from typing import Dict

from voice_dna import VoiceDNA


class IVoiceDNAFilter(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def priority(self) -> int:
        pass

    @abstractmethod
    def process(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict) -> bytes:
        pass
