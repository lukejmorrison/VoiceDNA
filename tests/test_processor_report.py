import io
import math
import struct
import wave

from voice_dna import VoiceDNA
from voicedna.framework import VoiceDNAProcessor


def _make_wav_bytes(duration_seconds: float = 0.1, sample_rate: int = 16000) -> bytes:
    frame_count = int(duration_seconds * sample_rate)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)
        wave_file.setframerate(sample_rate)

        for index in range(frame_count):
            sample = int(32767 * 0.25 * math.sin(2 * math.pi * 440 * index / sample_rate))
            wave_file.writeframesraw(struct.pack("<h", sample))
    return buffer.getvalue()


def test_processor_generates_report_with_filter_details():
    dna = VoiceDNA.create_new("Report voice", "report")
    processor = VoiceDNAProcessor()

    output = processor.process(_make_wav_bytes(), dna, {"force_age": 12, "audio_format": "wav"})

    assert isinstance(output, bytes)
    report = processor.get_last_report()
    assert "filters" in report
    assert "total_duration_ms" in report
    assert report["filter_count"] >= 1
    assert isinstance(report["filters"], list)
    assert all("name" in item and "status" in item for item in report["filters"])
