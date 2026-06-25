"""Hashing utility tests."""

from app.utils.hashing import generate_content_hash


def test_identical_content_produces_identical_hashes() -> None:
    """Canonical hash generation is deterministic."""
    first = generate_content_hash("Delta Update", "Summary", "Content")
    second = generate_content_hash("Delta Update", "Summary", "Content")

    assert first == second
    assert len(first) == 64


def test_different_content_produces_different_hashes() -> None:
    """Content changes produce different SHA-256 hashes."""
    first = generate_content_hash("Delta Update", "Summary", "Content")
    second = generate_content_hash("Delta Update", "Summary", "Different content")

    assert first != second


def test_hash_normalizes_title_and_whitespace() -> None:
    """Minor title punctuation and casing differences normalize consistently."""
    first = generate_content_hash("Delta   Update!", " Summary ", " Content ")
    second = generate_content_hash("delta update", "summary", "content")

    assert first == second