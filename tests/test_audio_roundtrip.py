import io
import wave

from voice_dna import VoiceDNA
from voicedna.framework import VoiceDNAProcessor


def test_audio_pipeline_changes_waveform_and_stays_wav(wav_fixture_bytes: bytes):
    dna = VoiceDNA.create_new("Roundtrip voice", "roundtrip")
    processor = VoiceDNAProcessor()

    output = processor.process(wav_fixture_bytes, dna, {"force_age": 15, "audio_format": "wav"})

    assert output != wav_fixture_bytes

    with wave.open(io.BytesIO(output), "rb") as wave_file:
        assert wave_file.getnchannels() == 1
        assert wave_file.getframerate() == 16000
        assert wave_file.getnframes() > 0
