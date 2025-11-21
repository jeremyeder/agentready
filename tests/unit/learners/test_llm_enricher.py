"""Tests for LLM enrichment functionality."""

import json
from unittest.mock import Mock

import pytest
from anthropic import Anthropic

from agentready.learners.llm_enricher import LLMEnricher
from agentready.models import Attribute, DiscoveredSkill, Finding, Repository


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client."""
    client = Mock(spec=Anthropic)

    # Mock response
    mock_response = Mock()
    mock_response.content = [
        Mock(
            text=json.dumps(
                {
                    "skill_description": "Enhanced description from LLM",
                    "instructions": [
                        "Step 1: Do something specific",
                        "Step 2: Verify it worked",
                        "Step 3: Commit the changes",
                    ],
                    "code_examples": [
                        {
                            "file_path": "src/example.py",
                            "code": "def example():\n    pass",
                            "explanation": "This shows the pattern",
                        }
                    ],
                    "best_practices": ["Always use type hints", "Test your code"],
                    "anti_patterns": [
                        "Don't use global variables",
                        "Avoid mutable defaults",
                    ],
                }
            )
        )
    ]

    client.messages.create.return_value = mock_response
    return client


@pytest.fixture
def basic_skill():
    """Basic skill from heuristic extraction."""
    return DiscoveredSkill(
        skill_id="test-skill",
        name="Test Skill",
        description="Basic description",
        confidence=95.0,
        source_attribute_id="test_attribute",
        reusability_score=100.0,
        impact_score=50.0,
        pattern_summary="Test pattern",
        code_examples=["Basic example"],
        citations=[],
    )


@pytest.fixture
def sample_repository(tmp_path):
    """Sample repository."""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()

    # Create .git directory
    (repo_path / ".git").mkdir()

    # Create a sample file
    (repo_path / "test.py").write_text("def test():\n    pass")

    return Repository(
        path=repo_path,
        name="test-repo",
        url=None,
        branch="main",
        commit_hash="abc123",
        languages={"Python": 1},
        total_files=1,
        total_lines=2,
    )


@pytest.fixture
def sample_finding():
    """Sample finding."""
    attr = Attribute(
        id="test_attribute",
        name="Test Attribute",
        category="Testing",
        tier=1,
        description="A test attribute",
        criteria="Must pass",
        default_weight=1.0,
    )

    return Finding(
        attribute=attr,
        status="pass",
        score=95.0,
        measured_value="passing",
        threshold="pass",
        evidence=["Test evidence 1", "Test evidence 2"],
        remediation=None,
        error_message=None,
    )


def test_enrich_skill_success(
    mock_anthropic_client, basic_skill, sample_repository, sample_finding, tmp_path
):
    """Test successful skill enrichment."""
    cache_dir = tmp_path / "cache"
    enricher = LLMEnricher(mock_anthropic_client, cache_dir=cache_dir)

    enriched = enricher.enrich_skill(basic_skill, sample_repository, sample_finding)

    # Verify API was called
    assert mock_anthropic_client.messages.create.called

    # Verify enrichment
    assert enriched.description == "Enhanced description from LLM"
    assert len(enriched.code_examples) > len(basic_skill.code_examples)


def test_enrich_skill_uses_cache(
    mock_anthropic_client, basic_skill, sample_repository, sample_finding, tmp_path
):
    """Test that second enrichment uses cache."""
    cache_dir = tmp_path / "cache"
    enricher = LLMEnricher(mock_anthropic_client, cache_dir=cache_dir)

    # First call
    enricher.enrich_skill(basic_skill, sample_repository, sample_finding)
    first_call_count = mock_anthropic_client.messages.create.call_count

    # Second call (should use cache)
    enricher.enrich_skill(basic_skill, sample_repository, sample_finding)
    second_call_count = mock_anthropic_client.messages.create.call_count

    # Verify cache was used
    assert second_call_count == first_call_count


def test_enrich_skill_api_error_fallback(
    basic_skill, sample_repository, sample_finding, tmp_path
):
    """Test fallback to original skill on API error."""
    client = Mock(spec=Anthropic)
    client.messages.create.side_effect = Exception("API Error")

    cache_dir = tmp_path / "cache"
    enricher = LLMEnricher(client, cache_dir=cache_dir)

    enriched = enricher.enrich_skill(basic_skill, sample_repository, sample_finding)

    # Should return original skill
    assert enriched.skill_id == basic_skill.skill_id
    assert enriched.description == basic_skill.description
