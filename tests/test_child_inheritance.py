import pytest

from voice_dna import VoiceDNA


def test_create_child_inherits_traits_and_embedding_shape():
    parent = VoiceDNA.create_new("Parent voice", "parent")
    child = parent.create_child("mini", inherit_strength=0.4)

    assert child.get_recognition_id().startswith("vdna_mini_")
    assert len(child.core_embedding) == len(parent.core_embedding)
    assert child.imprint_strength == 0.4
    assert set(parent.unique_traits).issubset(set(child.unique_traits))


def test_create_child_rejects_invalid_strength():
    parent = VoiceDNA.create_new("Parent voice", "parent")

    with pytest.raises(ValueError):
        parent.create_child("mini", inherit_strength=-0.1)

    with pytest.raises(ValueError):
        parent.create_child("mini", inherit_strength=1.1)


def test_create_child_rejects_empty_name():
    parent = VoiceDNA.create_new("Parent voice", "parent")

    with pytest.raises(ValueError):
        parent.create_child("", inherit_strength=0.4)
