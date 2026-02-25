from pathlib import Path

from voicedna.providers.piper import _model_preference_score, _resolve_prosody_for_text


def test_model_preference_score_prefers_medium_english_voice():
    strong = Path("en_US-lessac-medium.onnx")
    weak = Path("de_DE-random-low.onnx")

    assert _model_preference_score(strong) > _model_preference_score(weak)


def test_notification_prosody_defaults_for_short_text(monkeypatch):
    monkeypatch.setenv("VOICEDNA_PIPER_NOTIFICATION_LENGTH_SCALE", "0.87")
    monkeypatch.setenv("VOICEDNA_PIPER_NOTIFICATION_NOISE_SCALE", "0.50")
    monkeypatch.setenv("VOICEDNA_PIPER_NOTIFICATION_NOISE_W", "0.70")

    length_scale, noise_scale, noise_w = _resolve_prosody_for_text(
        text="VoiceDNA quick test notification.",
        length_scale=0.92,
        noise_scale=0.60,
        noise_w=0.78,
    )

    assert length_scale == 0.87
    assert noise_scale == 0.50
    assert noise_w == 0.70


def test_notification_prosody_keeps_base_for_long_text():
    long_text = "This is a longer phrase intended to avoid the short-notification path because it exceeds one hundred characters in total length for testing."

    length_scale, noise_scale, noise_w = _resolve_prosody_for_text(
        text=long_text,
        length_scale=0.92,
        noise_scale=0.60,
        noise_w=0.78,
    )

    assert length_scale == 0.92
    assert noise_scale == 0.60
    assert noise_w == 0.78
