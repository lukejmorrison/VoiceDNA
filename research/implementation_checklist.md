# VoiceDNA → OpenClaw Implementation Checklist

1. **Inventory repo surface**
   - Confirm actual VoiceDNA package layout, example folders, and test harness.
   - Output: exact files to edit and any missing directories.

2. **Define adapter API**
   - Specify `VoiceAdapter.select_preset()` and `VoiceAdapter.synthesize()` signatures.
   - Decide whether config comes from JSON/TOML/YAML or in-memory dict.

3. **Add preset registry**
   - Register pilot presets: `neutral`, `friendly`, `flair`.
   - Document fallback/default behavior.

4. **Implement agent mapping resolution**
   - Map `agent_id` first, then `agent_name`, then default preset.
   - Ensure deterministic behavior and clear errors for unknown presets.

5. **Build OpenClaw demo**
   - Create `examples/openclaw_voicedemo.py` showing 3 agents speaking with different presets.
   - Keep the demo local-first and easy to run.

6. **Wire configuration**
   - Add an opt-in config example for per-agent voice routing.
   - Keep existing CLI/SDK behavior unchanged unless config is enabled.

7. **Add unit tests for selection logic**
   - Cover explicit mapping, alias fallback, and default preset resolution.

8. **Add smoke test for synthesis**
   - Verify output file/bytes are generated for at least one preset.

9. **Document usage**
   - Update README or add a short usage guide with example commands and config.

10. **Check licensing / asset compatibility**
    - Verify preset voices and any bundled assets are allowed for the target usage.
    - Flag any restrictions before shipping.

11. **Validate packaging / deps**
    - Confirm `pyproject.toml` includes any required runtime/test dependencies.
    - Keep dependency additions minimal.

12. **Prepare handoff for implementation**
    - Give Dr Voss a branch name and ticket-sized file targets.
    - Suggested branch: `feature/voicedna-openclaw-per-agent-voices`
