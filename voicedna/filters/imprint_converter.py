import io
import os
import tempfile
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
        params["imprint_converter.rvc_mode"] = "disabled"
        params["imprint_converter.consistency_threshold"] = float(params.get("imprint_converter.consistency_threshold", 0.92))
        params["imprint_converter.consistency_enabled"] = bool(params.get("imprint_converter.consistency_enabled", True))

        mode = params.get("imprint_converter.mode", "simple")
        params["imprint_converter.mode"] = mode

        if mode == "rvc":
            converted = self._process_rvc(audio_bytes, dna, params)
            return self._enforce_consistency(converted, dna, params)

        if mode == "rvc_stub":
            params["imprint_converter.rvc_note"] = "RVC stub path selected; using placeholder conversion"
            params["imprint_converter.rvc_mode"] = "stub"
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

    def _process_rvc(self, audio_bytes: bytes, dna: VoiceDNA, params: Dict) -> bytes:
        """
        Real RVC mode.

        Required params for quality cloning:
        - imprint_converter.rvc_model_path: path to .pth RVC model
        - imprint_converter.rvc_reference_path: path to reference speaker WAV

        Optional params:
        - imprint_converter.rvc_index_path: path to .index file
        - imprint_converter.rvc_device: "cpu" or "cuda:0"
        - imprint_converter.rvc_pitch: integer semitone shift
        """
        params["imprint_converter.rvc_backend"] = params.get("imprint_converter.rvc_backend", "rvc-python")
        params["imprint_converter.rvc_reference_path"] = params.get(
            "imprint_converter.rvc_reference_path",
            dna.imprint_source,
        )
        params["imprint_converter.rvc_embedding_dims"] = len(dna.core_embedding)

        model_path = params.get("imprint_converter.rvc_model_path")
        if not model_path:
            params["imprint_converter.rvc_mode"] = "fallback"
            params["imprint_converter.rvc_note"] = (
                "RVC mode requested, but no model path was provided. "
                "Set params['imprint_converter.rvc_model_path'] to your .pth model file."
            )
            return audio_bytes

        if not os.path.exists(model_path):
            params["imprint_converter.rvc_mode"] = "fallback"
            params["imprint_converter.rvc_note"] = f"RVC model file not found: {model_path}"
            return audio_bytes

        index_path = params.get("imprint_converter.rvc_index_path")
        if index_path and not os.path.exists(index_path):
            params["imprint_converter.rvc_index_path"] = None
            params["imprint_converter.rvc_note"] = f"RVC index file not found, continuing without index: {index_path}"

        reference_path = params.get("imprint_converter.rvc_reference_path")
        if not reference_path or not os.path.exists(reference_path):
            params["imprint_converter.rvc_mode"] = "fallback"
            params["imprint_converter.rvc_note"] = (
                "RVC reference audio missing. Set params['imprint_converter.rvc_reference_path'] "
                "to a WAV sample of the target voice."
            )
            return audio_bytes

        try:
            wav_input = self._ensure_wav_bytes(audio_bytes, params)
            with tempfile.TemporaryDirectory(prefix="voicedna_rvc_") as temp_dir:
                input_path = os.path.join(temp_dir, "input.wav")
                output_path = os.path.join(temp_dir, "output.wav")

                with open(input_path, "wb") as input_file:
                    input_file.write(wav_input)

                self._run_rvc_python(
                    input_path=input_path,
                    output_path=output_path,
                    model_path=model_path,
                    index_path=params.get("imprint_converter.rvc_index_path"),
                    reference_path=reference_path,
                    device=params.get("imprint_converter.rvc_device", "cpu"),
                    pitch=int(params.get("imprint_converter.rvc_pitch", 0)),
                )

                if not os.path.exists(output_path):
                    raise RuntimeError("RVC backend completed but produced no output file")

                with open(output_path, "rb") as output_file:
                    converted_wav = output_file.read()

            params["imprint_converter.rvc_mode"] = "active"
            params["imprint_converter.rvc_note"] = "RVC conversion active via rvc-python backend"
            return self._restore_format(converted_wav, params)
        except Exception as error:
            params["imprint_converter.rvc_mode"] = "fallback"
            params["imprint_converter.rvc_error"] = str(error)
            params["imprint_converter.rvc_note"] = (
                "RVC backend failed; falling back to non-RVC processing. "
                "Install with pip install \"voicedna[rvc]\" and verify model/reference paths."
            )
            return audio_bytes

    def _run_rvc_python(
        self,
        input_path: str,
        output_path: str,
        model_path: str,
        index_path: str | None,
        reference_path: str,
        device: str,
        pitch: int,
    ) -> None:
        from rvc_python.infer import RVCInference

        engine = RVCInference(device=device)

        try:
            if index_path:
                try:
                    engine.load_model(model_path, index_path=index_path)
                except TypeError:
                    engine.load_model(model_path, index_path)
            else:
                engine.load_model(model_path)
        except TypeError:
            engine.load_model(model_name=model_path)

        inference_attempts = [
            {"input_audio_path": input_path, "output_audio_path": output_path, "f0up_key": pitch, "speaker_wav": reference_path},
            {"input_audio_path": input_path, "output_audio_path": output_path, "pitch": pitch, "speaker_wav": reference_path},
            {"input_audio_path": input_path, "output_audio_path": output_path, "speaker_wav": reference_path},
            {"input_path": input_path, "output_path": output_path, "f0up_key": pitch, "speaker_wav": reference_path},
            {"input_path": input_path, "output_path": output_path, "pitch": pitch, "speaker_wav": reference_path},
        ]

        last_error: Exception | None = None
        for kwargs in inference_attempts:
            try:
                engine.infer_file(**kwargs)
                return
            except TypeError as error:
                last_error = error
                continue

        if last_error:
            raise last_error
        raise RuntimeError("Unable to run rvc_python inference for provided arguments")

    def _ensure_wav_bytes(self, audio_bytes: bytes, params: Dict) -> bytes:
        audio_format = params.get("audio_format", "wav")
        if audio_format == "wav":
            return audio_bytes

        from pydub import AudioSegment

        segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format=audio_format)
        output = io.BytesIO()
        segment.export(output, format="wav")
        return output.getvalue()

    def _restore_format(self, audio_bytes: bytes, params: Dict) -> bytes:
        audio_format = params.get("audio_format", "wav")
        if audio_format == "wav":
            return audio_bytes

        from pydub import AudioSegment

        segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
        output = io.BytesIO()
        segment.export(output, format=audio_format)
        return output.getvalue()

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
