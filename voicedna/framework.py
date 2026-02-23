from __future__ import annotations

from importlib import metadata
from typing import Dict, List

from voice_dna import VoiceDNA

from .plugins.base import IVoiceDNAFilter


class VoiceDNAProcessor:
    def __init__(self):
        self.filters: List[IVoiceDNAFilter] = []
        self.load_plugins()

    def register_filter(self, plugin: IVoiceDNAFilter):
        self.filters.append(plugin)
        self.filters.sort(key=lambda filter_plugin: filter_plugin.priority())

    def load_plugins(self):
        self._load_plugins_from_group("voicedna.filters")
        self._load_plugins_from_group("voicedna.plugins")

    def _load_plugins_from_group(self, group: str):
        try:
            discovered = metadata.entry_points(group=group)
        except TypeError:
            discovered = metadata.entry_points().select(group=group)

        for entrypoint in discovered:
            try:
                plugin_factory = entrypoint.load()
                plugin = plugin_factory() if callable(plugin_factory) else plugin_factory
                self.register_filter(plugin)
            except Exception:
                continue

    def process(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict | None = None) -> bytes:
        current_audio = audio_bytes
        process_params = params or {}
        for filter_obj in self.filters:
            current_audio = filter_obj.process(current_audio, dna, process_params)
        return current_audio

    def get_filter_names(self) -> List[str]:
        return [filter_obj.name() for filter_obj in self.filters]
