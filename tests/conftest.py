import io
import math
import struct
import wave

import pytest


@pytest.fixture()
def wav_fixture_bytes() -> bytes:
    sample_rate = 16000
    duration_seconds = 0.2
    frame_count = int(sample_rate * duration_seconds)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)
        wave_file.setframerate(sample_rate)

        for index in range(frame_count):
            sample = int(32767 * 0.35 * math.sin(2 * math.pi * 440 * index / sample_rate))
            wave_file.writeframesraw(struct.pack("<h", sample))

    return buffer.getvalue()
