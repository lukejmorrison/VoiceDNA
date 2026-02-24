from __future__ import annotations

from importlib import metadata
import logging
import time
from typing import Any, Dict, List

from voice_dna import VoiceDNA

from .filters import AgeMaturationFilter, ImprintConverterFilter
from .plugins.base import IVoiceDNAFilter


logger = logging.getLogger("VoiceDNA")


class VoiceDNAProcessor:
    def __init__(self):
        self.filters: List[IVoiceDNAFilter] = []
        self.last_metrics: Dict[str, float] = {}
        self.last_report: Dict[str, Any] = {}
        self.load_plugins()

    def register_filter(self, plugin: IVoiceDNAFilter):
        plugin_name = plugin.name()
        if plugin_name in self.get_filter_names():
            return
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
        chain_started_at = time.perf_counter()
        current_audio = audio_bytes
        process_params = params or {}
        metrics: Dict[str, float] = {}
        report_filters: List[Dict[str, Any]] = []

        for filter_obj in self.filters:
            started_at = time.perf_counter()
            try:
                current_audio = filter_obj.process(current_audio, dna, process_params)
            except Exception as error:
                logger.warning("Filter %s failed: %s", filter_obj.name(), error)
                report_filters.append(
                    {
                        "name": filter_obj.name(),
                        "status": "error",
                        "duration_ms": round((time.perf_counter() - started_at) * 1000, 3),
                        "error": str(error),
                    }
                )
                continue
            duration_seconds = time.perf_counter() - started_at
            metrics[filter_obj.name()] = duration_seconds
            report_filters.append(
                {
                    "name": filter_obj.name(),
                    "status": "ok",
                    "duration_ms": round(duration_seconds * 1000, 3),
                }
            )

        self.last_metrics = metrics
        self.last_report = {
            "filters": report_filters,
            "filter_count": len(self.filters),
            "total_duration_ms": round((time.perf_counter() - chain_started_at) * 1000, 3),
            "input_bytes": len(audio_bytes),
            "output_bytes": len(current_audio),
            "consistency_score": process_params.get("imprint_converter.consistency_score"),
            "rvc_ready": bool(process_params.get("imprint_converter.rvc_ready", False)),
            "rvc_mode": process_params.get("imprint_converter.rvc_mode", "disabled"),
            "imprint_converter": {
                "mode": process_params.get("imprint_converter.mode", "simple"),
                "rvc_ready": bool(process_params.get("imprint_converter.rvc_ready", False)),
                "rvc_mode": process_params.get("imprint_converter.rvc_mode", "disabled"),
                "consistency_score": process_params.get("imprint_converter.consistency_score"),
                "consistency_corrected": bool(process_params.get("imprint_converter.consistency_corrected", False)),
                "watermark_applied": bool(process_params.get("imprint_converter.watermark_applied", False)),
                "rvc_note": process_params.get("imprint_converter.rvc_note"),
            },
        }
        return current_audio

    def get_filter_names(self) -> List[str]:
        return [filter_obj.name() for filter_obj in self.filters]

    def get_last_report(self) -> Dict[str, Any]:
        return self.last_report
