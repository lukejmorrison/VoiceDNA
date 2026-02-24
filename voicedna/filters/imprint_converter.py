import io
from typing import Dict

from voice_dna import VoiceDNA

from .audio_helpers import imprint_mix_wav_bytes
from ..consistency import VoiceConsistencyEngine
from ..plugins.base import IVoiceDNAFilter


class ImprintConverterFilter(IVoiceDNAFilter):
    def name(self) -> str:
        return "ImprintConverter"

    def priority(self) -> int:
        return 20

    def process(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict) -> bytes:
        strength = max(0.0, min(1.0, dna.imprint_strength))
        params["imprint_converter.strength"] = strength
        params["imprint_converter.source"] = dna.imprint_source
        params["imprint_converter.rvc_ready"] = True
        params["imprint_converter.consistency_threshold"] = float(params.get("imprint_converter.consistency_threshold", 0.92))
        params["imprint_converter.consistency_enabled"] = bool(params.get("imprint_converter.consistency_enabled", True))

        mode = params.get("imprint_converter.mode", "simple")
        params["imprint_converter.mode"] = mode

        if mode == "rvc_stub":
            params["imprint_converter.rvc_note"] = "RVC stub path selected; using placeholder conversion"
            converted = self._process_rvc_stub(audio_bytes, dna, params)
            return self._enforce_consistency(converted, dna, params)

        audio_format = params.get("audio_format", "wav")
        try:
            from pydub import AudioSegment

            source = AudioSegment.from_file(io.BytesIO(audio_bytes), format=audio_format)
            wet_gain_db = -18 + (12 * strength)
            wet = source.apply_gain(wet_gain_db)
            mixed = source.overlay(wet, gain_during_overlay=-(6 - 4 * strength))
            output = io.BytesIO()
            mixed.export(output, format=audio_format)
            converted = output.getvalue()
            return self._enforce_consistency(converted, dna, params)
        except Exception as error:
            params["imprint_converter.error"] = str(error)
            if audio_format == "wav":
                try:
                    converted = imprint_mix_wav_bytes(audio_bytes, strength)
                    return self._enforce_consistency(converted, dna, params)
                except Exception as fallback_error:
                    params["imprint_converter.fallback_error"] = str(fallback_error)
            return audio_bytes

    def _enforce_consistency(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict) -> bytes:
        if not params.get("imprint_converter.consistency_enabled", True):
            return audio_bytes

        threshold = float(params.get("imprint_converter.consistency_threshold", 0.92))
        engine = VoiceConsistencyEngine(threshold=threshold)
        output_audio, score, rvc_ready, correction_applied = engine.enforce_consistency(
            audio_bytes,
            dna.core_embedding,
            dna.voice_fingerprint_id,
        )

        params["imprint_converter.consistency_score"] = round(score, 4)
        params["imprint_converter.rvc_ready"] = rvc_ready
        params["imprint_converter.consistency_corrected"] = correction_applied
        params["imprint_converter.watermark_applied"] = output_audio != audio_bytes
        if correction_applied and params.get("imprint_converter.rvc_note") is None:
            params["imprint_converter.rvc_note"] = "Applied gentle parametric correction to reinforce core voice identity"
        return output_audio

    def _process_rvc_stub(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict) -> bytes:
        """
        RVC upgrade path (stub):

        1. Load or create a reference voice profile from imprint audio.
           - Example config key: params["imprint_converter.rvc_reference_path"]
        2. Convert input audio using an RVC backend (e.g. rvc-python / fairseq wrapper).
        3. Match model/feature embedding with dna.core_embedding (256-dim identity vector)
           to keep conversion anchored to the persistent VoiceDNA fingerprint.
        4. Return converted bytes in the same audio format expected by the pipeline.

        This placeholder keeps current behavior stable while making the integration point explicit.
        """
        params["imprint_converter.rvc_embedding_dims"] = len(dna.core_embedding)
        params["imprint_converter.rvc_reference_path"] = params.get(
            "imprint_converter.rvc_reference_path",
            "<set-path-to-imprint-reference-audio>",
        )
        params["imprint_converter.rvc_backend"] = params.get("imprint_converter.rvc_backend", "rvc-python")
        return audio_bytes
