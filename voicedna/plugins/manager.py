from importlib import metadata
from typing import Dict, List, Tuple

from voice_dna import VoiceDNA

from .base import IVoiceDNAFilter


class PluginManager:
    def __init__(self):
        self._filters: List[IVoiceDNAFilter] = []

    def register(self, plugin: IVoiceDNAFilter):
        self._filters.append(plugin)
        self._filters.sort(key=lambda filter_plugin: filter_plugin.priority())

    def load_entrypoint_plugins(self, group: str = "voicedna.plugins") -> Tuple[List[str], List[str]]:
        loaded: List[str] = []
        failed: List[str] = []

        try:
            discovered = metadata.entry_points(group=group)
        except TypeError:
            discovered = metadata.entry_points().select(group=group)

        for entrypoint in discovered:
            try:
                plugin_factory = entrypoint.load()
                plugin = plugin_factory() if callable(plugin_factory) else plugin_factory
                self.register(plugin)
                loaded.append(entrypoint.name)
            except Exception:
                failed.append(entrypoint.name)

        return loaded, failed

    def list_plugins(self) -> List[str]:
        return [plugin.name() for plugin in self._filters]

    def process(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict | None = None) -> bytes:
        current_audio = audio_bytes
        process_params = params or {}
        for plugin in self._filters:
            current_audio = plugin.process(current_audio, dna, process_params)
        return current_audio
