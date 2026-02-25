from voicedna.synthesis import detect_natural_backend_decision


def test_detect_natural_backend_lowvram_auto_on_8gb(monkeypatch):
    monkeypatch.setenv("VOICEDNA_SIMULATED_VRAM_GB", "8")
    monkeypatch.setenv("VOICEDNA_MIN_PERSONAPLEX_VRAM_GB", "12")

    decision = detect_natural_backend_decision()

    assert decision.backend == "personaplex"
    assert decision.low_vram_mode is True
    assert "loading 4-bit PersonaPlex" in decision.status_message


def test_detect_natural_backend_full_mode_on_24gb(monkeypatch):
    monkeypatch.setenv("VOICEDNA_SIMULATED_VRAM_GB", "24")
    monkeypatch.setenv("VOICEDNA_MIN_PERSONAPLEX_VRAM_GB", "12")

    decision = detect_natural_backend_decision()

    assert decision.backend == "personaplex"
    assert decision.low_vram_mode is False


def test_detect_natural_backend_lowvram_forced_without_vram(monkeypatch):
    monkeypatch.delenv("VOICEDNA_SIMULATED_VRAM_GB", raising=False)

    decision = detect_natural_backend_decision(force_low_vram=True)

    assert decision.backend == "personaplex"
    assert decision.low_vram_mode is True
    assert "low-VRAM mode" in decision.status_message
