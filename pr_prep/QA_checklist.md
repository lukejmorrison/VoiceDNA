# QA Checklist — VoiceDNA per-agent voice pilot

## Prereqs
- Checkout branch: `feature/voicedna-openclaw-per-agent-voices`
- Local backend available if you want demo synthesis to run fully (`voice_dna` + dependencies)
- Optional opt-in env:
  - `VOICEDNA_OPENCLAW_PRESETS=1`
  - `VOICEDNA_OPENCLAW_PRESETS_MAP` (only if testing custom routing)

## Test plan
1. **Run the focused adapter tests**
   ```bash
   cd /path/to/VoiceDNA
   python -m pytest tests/test_voice_adapter.py -v
   ```
   **Expected:** tests pass; preset selection, env loading, and synthesis guards are covered.

2. **Run the local demo**
   ```bash
   VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
   ```
   **Expected:** the script logs the three agents and resolves these presets:
   - `agent:namshub` → `neutral`
   - `agent:david-hardman` → `friendly`
   - `agent:dr-voss-thorne` → `flair`

3. **Confirm demo audio files exist**
   ```bash
   ls -lh examples/openclaw/output/*.wav
   ```
   **Expected:** these files exist and are non-empty:
   - `examples/openclaw/output/namshub_neutral.wav`
   - `examples/openclaw/output/david_friendly.wav`
   - `examples/openclaw/output/voss_flair.wav`

4. **Play back the demos**
   - Open each WAV file in a local media player, or use any preview app.
   - Listen for clearly different voice characteristics across the three personas.
   **Expected:** three distinct-sounding outputs, one per agent/preset pair.

5. **Check fallback behavior**
   - Set a test mapping for an unknown agent or preset.
   - Re-run the demo or adapter test.
   **Expected:** unknown preset names fail clearly; unknown agents fall back to the default preset.

6. **Validate no unintended changes**
   ```bash
   git status --short
   ```
   **Expected:** only the intended pilot files and generated demo artifacts are present.

## Pass criteria
- Focused tests pass.
- Demo runs in a backend-complete environment.
- WAV files are created, readable, and non-empty.
- Routing matches the deterministic order: `agent_id` → `agent_name` → default.
