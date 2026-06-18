"""Tests for Vector RAG knowledge retrieval."""

import tempfile
import json
from pathlib import Path

import pytest
from src.retrieval.vector_rag import VectorRAG, KnowledgeEntry, BUILTIN_KNOWLEDGE


@pytest.fixture
def rag():
    r = VectorRAG()
    r.add_builtin()
    r.index_knowledge()
    return r


def test_builtin_knowledge(rag):
    """Built-in knowledge is loaded."""
    assert len(rag.entries) >= 14


def test_search_finds_relevant(rag):
    """Search returns relevant results."""
    results = rag.search("shaft torsion", top_k=3)
    assert len(results) > 0
    assert results[0].score > 0


def test_search_by_domain(rag):
    """Search can be filtered by domain."""
    results = rag.search("thermal", domain="termo", top_k=5)
    if results:
        assert all(r.entry.domain == "termo" for r in results)


def test_search_empty_query(rag):
    """Empty query returns empty results (or low-relevance)."""
    results = rag.search("", top_k=5)
    assert isinstance(results, list)


def test_get_entry(rag):
    """Get entry by ID."""
    entry = rag.get_entry("K001")
    assert entry is not None
    assert "shaft" in entry.title.lower()


def test_get_entry_not_found(rag):
    """Unknown ID returns None."""
    assert rag.get_entry("NONEXISTENT") is None


def test_list_domains(rag):
    """List domains returns all unique domains."""
    domains = rag.list_domains()
    assert "mecanica" in domains
    assert "fluidos" in domains
    assert "termo" in domains
    assert len(domains) >= 8


def test_add_custom_entry():
    """Custom entries can be added."""
    rag = VectorRAG()
    entry = KnowledgeEntry("C001", "Custom", "Test content", "test")
    rag.add_entry(entry)
    rag.index_knowledge()
    assert rag.get_entry("C001") is not None


def test_quality_scores():
    """All built-in entries have quality_scores."""
    for entry in BUILTIN_KNOWLEDGE:
        assert 0 <= entry.quality_score <= 10, f"{entry.id} has invalid score"


def test_load_from_directory(tmp_path):
    """Load from directory loads JSON files."""
    rag = VectorRAG(knowledge_dir=str(tmp_path))
    data = [{"id": "F1", "title": "Fourier", "content": "q=-k*dT/dx"}]
    (tmp_path / "physics.json").write_text(json.dumps(data))
    count = rag.load_from_directory()
    assert count == 1
