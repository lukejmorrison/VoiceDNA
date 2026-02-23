from typing import Dict, List

from voice_dna import VoiceDNA

from .base import IVoiceDNAFilter


class PluginManager:
    def __init__(self):
        self._filters: List[IVoiceDNAFilter] = []

    def register(self, plugin: IVoiceDNAFilter):
        self._filters.append(plugin)
        self._filters.sort(key=lambda filter_plugin: filter_plugin.priority())

    def list_plugins(self) -> List[str]:
        return [plugin.name() for plugin in self._filters]

    def process(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict | None = None) -> bytes:
        current_audio = audio_bytes
        process_params = params or {}
        for plugin in self._filters:
            current_audio = plugin.process(current_audio, dna, process_params)
        return current_audio
