from __future__ import annotations

from importlib import metadata
import logging
import time
from typing import Dict, List

from voice_dna import VoiceDNA

from .filters import AgeMaturationFilter, ImprintConverterFilter
from .plugins.base import IVoiceDNAFilter


logger = logging.getLogger("VoiceDNA")


class VoiceDNAProcessor:
    def __init__(self):
        self.filters: List[IVoiceDNAFilter] = []
        self.last_metrics: Dict[str, float] = {}
        self.load_plugins()

    def register_filter(self, plugin: IVoiceDNAFilter):
        self.filters.append(plugin)
        self.filters.sort(key=lambda filter_plugin: filter_plugin.priority())

    def load_plugins(self):
        self._register_builtin_filters()
        self._load_plugins_from_group("voicedna.filters")
        self._load_plugins_from_group("voicedna.plugins")

    def _register_builtin_filters(self):
        self.register_filter(AgeMaturationFilter())
        self.register_filter(ImprintConverterFilter())

    def _load_plugins_from_group(self, group: str):
        try:
            discovered = metadata.entry_points(group=group)
        except TypeError:
            discovered = metadata.entry_points().select(group=group)

        for entrypoint in discovered:
            try:
                plugin_factory = entrypoint.load()
                plugin = plugin_factory() if callable(plugin_factory) else plugin_factory
                plugin_name = plugin.name()
                if plugin_name in self.get_filter_names():
                    continue
                self.register_filter(plugin)
            except Exception as error:
                logger.warning("Failed loading plugin %s from %s: %s", entrypoint.name, group, error)
                continue

    def process(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict | None = None) -> bytes:
        current_audio = audio_bytes
        process_params = params or {}
        metrics: Dict[str, float] = {}

        for filter_obj in self.filters:
            started_at = time.perf_counter()
            try:
                current_audio = filter_obj.process(current_audio, dna, process_params)
            except Exception as error:
                logger.warning("Filter %s failed: %s", filter_obj.name(), error)
                continue
            metrics[filter_obj.name()] = time.perf_counter() - started_at

        self.last_metrics = metrics
        return current_audio

    def get_filter_names(self) -> List[str]:
        return [filter_obj.name() for filter_obj in self.filters]
