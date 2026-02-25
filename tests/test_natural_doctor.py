from voicedna.synthesis import inspect_natural_backend_health


def test_natural_doctor_prefers_personaplex_when_ready(monkeypatch):
    monkeypatch.setenv("VOICEDNA_SIMULATED_VRAM_GB", "8")
    monkeypatch.setenv("VOICEDNA_MIN_PERSONAPLEX_VRAM_GB", "12")
    monkeypatch.setattr("voicedna.synthesis.check_personaplex_runtime", lambda low_vram: (True, "ok"))
    monkeypatch.setattr(
        "voicedna.synthesis.check_piper_runtime",
        lambda model_path=None: (True, "piper ok", "/tmp/voice.onnx"),
    )

    report = inspect_natural_backend_health()

    assert report.decision.low_vram_mode is True
    assert report.personaplex_available is True
    assert report.piper_available is True
    assert report.recommended_backend == "personaplex"


def test_natural_doctor_falls_back_to_piper_when_personaplex_unavailable(monkeypatch):
    monkeypatch.setenv("VOICEDNA_SIMULATED_VRAM_GB", "8")
    monkeypatch.setenv("VOICEDNA_MIN_PERSONAPLEX_VRAM_GB", "12")
    monkeypatch.setattr("voicedna.synthesis.check_personaplex_runtime", lambda low_vram: (False, "sm_61 unsupported"))
    monkeypatch.setattr(
        "voicedna.synthesis.check_piper_runtime",
        lambda model_path=None: (True, "piper ok", "/tmp/voice.onnx"),
    )

    report = inspect_natural_backend_health()

    assert report.personaplex_available is False
    assert report.piper_available is True
    assert report.recommended_backend == "piper"
    assert report.piper_model_path == "/tmp/voice.onnx"
