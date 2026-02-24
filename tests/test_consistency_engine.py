import io
import math
import struct
import wave

from voicedna.consistency import VoiceConsistencyEngine, cosine_similarity


def _make_wav_bytes(duration_seconds: float = 0.1, sample_rate: int = 16000) -> bytes:
    frame_count = int(duration_seconds * sample_rate)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)
        wave_file.setframerate(sample_rate)

        for index in range(frame_count):
            sample = int(32767 * 0.15 * math.sin(2 * math.pi * 220 * index / sample_rate))
            wave_file.writeframesraw(struct.pack("<h", sample))
    return buffer.getvalue()


def test_consistency_engine_fallback_extract_and_enforce():
    engine = VoiceConsistencyEngine()
    core = engine.extract_embedding_from_imprint("Synthetic imprint source", dims=256)

    audio_bytes = _make_wav_bytes()
    processed, score, rvc_ready, correction_applied = engine.enforce_consistency(
        audio_bytes,
        core,
        "vdna_test_001",
    )

    assert len(core) == 256
    assert isinstance(score, float)
    assert isinstance(rvc_ready, bool)
    assert isinstance(correction_applied, bool)
    assert isinstance(processed, bytes)
    assert len(processed) > 0


def test_cosine_similarity_handles_shape_mismatch():
    score = cosine_similarity([1.0, 0.0, 1.0], [1.0, 0.0])
    assert isinstance(score, float)
