# Ticket-sized tasks for Dr Voss

Branch: `feature/voicedna-openclaw-live-seam`

## 1) Wire the canonical live seam
**Files:** `tools/voicedna_tts_hook.py`, `tools/voicedna_adapter.py`
**Goal:** route output through `VoiceAdapter` when `VOICEDNA_OPENCLAW_PRESETS=1`, otherwise preserve current TTS behavior.
**Minimal repro:**
```bash
cd /home/namshub/dev/openclaw
python -m pytest tests/test_voicedna_tts_hook.py -v
```

## 2) Pass agent identity through the live reply path
**Files:** `skills/audio-responder-tts/audio_tts_reply.sh`, `tools/voicedna_tts_hook.py`
**Goal:** ensure `agent_id` and optional `agent_name` reach the hook.
**Minimal repro:**
```bash
cd /home/namshub/dev/openclaw
python -m pytest tests/test_voicedna_tts_hook.py -v
```

## 3) Harden opt-in and fallback semantics
**Files:** `tests/test_voicedna_adapter.py`, `tests/test_voicedna_e2e.py`, `tools/voicedna_adapter.py`
**Goal:** confirm env gating, preset-map parsing, and no-crash fallback behavior.
**Minimal repro:**
```bash
cd /home/namshub/dev/openclaw
python -m pytest tests/test_voicedna_adapter.py tests/test_voicedna_e2e.py -v
```

## 4) Remove stale path assumptions from docs
**Files:** `README.md`, `VOICEDNA_RUNBOOK.md`, `DESIGN_DOC_voicedna.md`, `skills/voicedna-agent-voices/SKILL.md`
**Goal:** document one canonical seam, the env flag, presets, and rollback.
**Minimal repro:**
```bash
rg -n "voicedna_tts_hook|VOICEDNA_OPENCLAW_PRESETS|openclaw_live_voice" README.md VOICEDNA_RUNBOOK.md DESIGN_DOC_voicedna.md skills/voicedna-agent-voices/SKILL.md
```

## 5) Resolve packaging/import-path shipping risk
**Files:** `tools/voicedna_adapter.py`, `pyproject.toml` or deploy docs
**Goal:** avoid depending on `/home/namshub/dev/VoiceDNA` being present at runtime.
**Minimal repro:**
```bash
cd /home/namshub/dev/openclaw
python -m pytest tests/test_voicedna_adapter.py -v
```
