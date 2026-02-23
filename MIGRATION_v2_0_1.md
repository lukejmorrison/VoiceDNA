# Migration Notes: v2.0.0 → v2.0.1

This patch hardens runtime behavior and packaging validation.

## What changed

- `VoiceDNAProcessor` now records a detailed chain report (`get_last_report()`) in addition to `last_metrics`.
- Filter registration now ignores duplicate filter names to prevent accidental double execution.
- `VoiceDNA.create_child()` now validates inputs strictly:
  - `child_user_name` must be non-empty.
  - `inherit_strength` must be between `0.0` and `1.0`.
  - parent/child embedding lengths must match.
- CI now validates editable install and package imports with `pip install -e .`.

## Impact

- Existing valid calls continue to work.
- Invalid `create_child()` inputs now raise `ValueError` instead of silently clamping.

## Recommended update checks

```bash
pip install -e .
python -c "from voicedna import VoiceDNA, VoiceDNAProcessor; print('ok')"
```
