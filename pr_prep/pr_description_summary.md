## PR #5 summary

This PR delivers an additive, opt-in OpenClaw voice pilot for VoiceDNA. It adds a small adapter that routes agents to presets deterministically (`agent_id` → `agent_name` → default), ships three pilot presets (`neutral`, `friendly`, `flair`), and includes a local demo plus targeted tests. Default VoiceDNA behavior is unchanged unless the feature is explicitly enabled.
