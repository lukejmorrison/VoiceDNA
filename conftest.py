"""Root conftest.py — ensures the project root is on sys.path so that
`voicedna` and `voice_dna` are importable during pytest collection without
requiring a prior `pip install -e .`."""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
