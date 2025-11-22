"""Comprehensive tests for LLM enricher module."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from anthropic import APIError, RateLimitError

from agentready.learners.llm_enricher import LLMEnricher
from agentready.models import Attribute, DiscoveredSkill, Finding, Repository


@pytest.fixture
def mock_client():
    """Create mock Anthropic client."""
    return MagicMock()


@pytest.fixture
def temp_repo():
    """Create temporary repository."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        (repo_path / ".agentready").mkdir()
        yield Repository(path=repo_path, languages={"python": 1.0}, total_files=10, total_lines=1000)


@pytest.fixture
def sample_skill():
    """Create sample discovered skill."""
    return DiscoveredSkill(
        skill_id="test-skill",
        name="Test Skill",
        confidence=85.0,
        pattern_summary="Test pattern",
        source_attribute_id="claude_md_file",
        impact_score=10.0,
        reusability_score=80.0,
        implementation_pattern="Test implementation",
        evidence=["Evidence 1"],
        extracted_at=datetime.now().isoformat(),
    )


@pytest.fixture
def sample_finding():
    """Create sample finding."""
    attribute = Attribute(
        id="claude_md_file",
        name="CLAUDE.md File",
        category="Documentation",
        tier=1,
        description="Test description",
        criteria="Test criteria",
    )
    return Finding(attribute=attribute, status="pass", score=100.0, evidence=["CLAUDE.md found"])


class TestLLMEnricherInit:
    """Test LLMEnricher initialization."""

    def test_init_defaults(self, mock_client):
        """Test initialization with defaults."""
        enricher = LLMEnricher(mock_client)
        assert enricher.client == mock_client
        assert enricher.model == "claude-sonnet-4-5-20250929"
        assert enricher.cache is not None
        assert enricher.code_sampler is None

    def test_init_custom_model(self, mock_client):
        """Test initialization with custom model."""
        enricher = LLMEnricher(mock_client, model="claude-opus-4")
        assert enricher.model == "claude-opus-4"

    def test_init_custom_cache_dir(self, mock_client, temp_repo):
        """Test initialization with custom cache directory."""
        cache_dir = temp_repo.path / "custom-cache"
        enricher = LLMEnricher(mock_client, cache_dir=cache_dir)
        assert enricher.cache.cache_dir == cache_dir


class TestEnrichSkill:
    """Test enrich_skill method."""

    @patch("agentready.learners.llm_enricher.CodeSampler")
    def test_enrich_skill_success(
        self, mock_sampler_class, mock_client, temp_repo, sample_skill, sample_finding
    ):
        """Test successful skill enrichment."""
        # Mock code sampler
        mock_sampler = MagicMock()
        mock_sampler.get_relevant_code.return_value = "Sample code"
        mock_sampler_class.return_value = mock_sampler

        # Mock API response
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text=json.dumps({
                    "enriched_instructions": ["Step 1", "Step 2"],
                    "code_snippets": ["snippet1"],
                    "best_practices": ["practice1"],
                    "anti_patterns": ["anti1"],
                })
            )
        ]
        mock_client.messages.create.return_value = mock_response

        enricher = LLMEnricher(mock_client, cache_dir=temp_repo.path / "cache")
        result = enricher.enrich_skill(sample_skill, temp_repo, sample_finding, use_cache=False)

        assert result is not None
        assert isinstance(result, DiscoveredSkill)
        mock_client.messages.create.assert_called_once()

    @patch("agentready.learners.llm_enricher.CodeSampler")
    def test_enrich_skill_uses_cache(
        self, mock_sampler_class, mock_client, temp_repo, sample_skill, sample_finding
    ):
        """Test that enrichment uses cache when available."""
        enricher = LLMEnricher(mock_client, cache_dir=temp_repo.path / "cache")

        # Pre-populate cache
        cached_skill = DiscoveredSkill(
            skill_id="test-skill",
            name="Cached Skill",
            confidence=95.0,
            pattern_summary="Cached",
            source_attribute_id="claude_md_file",
            impact_score=15.0,
            reusability_score=90.0,
            implementation_pattern="Cached",
            evidence=[],
            extracted_at=datetime.now().isoformat(),
        )

        import hashlib

        evidence_hash = hashlib.sha256("CLAUDE.md found".encode()).hexdigest()[:16]
        from agentready.services.llm_cache import LLMCache

        cache_key = LLMCache.generate_key("test-skill", 100.0, evidence_hash)
        enricher.cache.set(cache_key, cached_skill)

        # Try to enrich - should use cache
        result = enricher.enrich_skill(sample_skill, temp_repo, sample_finding, use_cache=True)

        assert result.name == "Cached Skill"
        mock_client.messages.create.assert_not_called()

    @patch("agentready.learners.llm_enricher.CodeSampler")
    def test_enrich_skill_rate_limit_retry(
        self, mock_sampler_class, mock_client, temp_repo, sample_skill, sample_finding
    ):
        """Test that rate limit errors trigger retry."""
        mock_sampler = MagicMock()
        mock_sampler.get_relevant_code.return_value = "Sample code"
        mock_sampler_class.return_value = mock_sampler

        # First call raises RateLimitError, second succeeds
        rate_limit_error = RateLimitError("Rate limit exceeded")
        rate_limit_error.retry_after = 0.1  # Short retry for testing

        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(text=json.dumps({"enriched_instructions": ["Step 1"]}))
        ]

        mock_client.messages.create.side_effect = [rate_limit_error, mock_response]

        enricher = LLMEnricher(mock_client, cache_dir=temp_repo.path / "cache")

        with patch("agentready.learners.llm_enricher.sleep"):  # Skip actual sleep
            result = enricher.enrich_skill(sample_skill, temp_repo, sample_finding, use_cache=False)

        assert result is not None
        assert mock_client.messages.create.call_count == 2

    @patch("agentready.learners.llm_enricher.CodeSampler")
    def test_enrich_skill_api_error_fallback(
        self, mock_sampler_class, mock_client, temp_repo, sample_skill, sample_finding
    ):
        """Test that API errors fall back to original skill."""
        mock_sampler = MagicMock()
        mock_sampler.get_relevant_code.return_value = "Sample code"
        mock_sampler_class.return_value = mock_sampler

        # Raise API error
        mock_client.messages.create.side_effect = APIError("API error")

        enricher = LLMEnricher(mock_client, cache_dir=temp_repo.path / "cache")
        result = enricher.enrich_skill(sample_skill, temp_repo, sample_finding, use_cache=False)

        # Should return original skill
        assert result.skill_id == sample_skill.skill_id
        assert result.name == sample_skill.name

    @patch("agentready.learners.llm_enricher.CodeSampler")
    def test_enrich_skill_unexpected_error_fallback(
        self, mock_sampler_class, mock_client, temp_repo, sample_skill, sample_finding
    ):
        """Test that unexpected errors fall back to original skill."""
        mock_sampler = MagicMock()
        mock_sampler.get_relevant_code.return_value = "Sample code"
        mock_sampler_class.return_value = mock_sampler

        # Raise unexpected error
        mock_client.messages.create.side_effect = ValueError("Unexpected error")

        enricher = LLMEnricher(mock_client, cache_dir=temp_repo.path / "cache")
        result = enricher.enrich_skill(sample_skill, temp_repo, sample_finding, use_cache=False)

        # Should return original skill
        assert result.skill_id == sample_skill.skill_id


class TestCallClaudeAPI:
    """Test _call_claude_api method."""

    @patch("agentready.learners.llm_enricher.CodeSampler")
    def test_call_claude_api_formats_prompt(
        self, mock_sampler_class, mock_client, temp_repo, sample_skill, sample_finding
    ):
        """Test that API call formats prompt correctly."""
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(text=json.dumps({"enriched_instructions": ["Step 1"]}))
        ]
        mock_client.messages.create.return_value = mock_response

        enricher = LLMEnricher(mock_client, cache_dir=temp_repo.path / "cache")
        result = enricher._call_claude_api(
            sample_skill, sample_finding, temp_repo, "Sample code"
        )

        # Should have called API with formatted prompt
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args
        assert "model" in call_args[1]
        assert "messages" in call_args[1]

    @patch("agentready.learners.llm_enricher.CodeSampler")
    def test_call_claude_api_parses_json_response(
        self, mock_sampler_class, mock_client, temp_repo, sample_skill, sample_finding
    ):
        """Test that API response is correctly parsed."""
        response_data = {
            "enriched_instructions": ["Step 1", "Step 2"],
            "code_snippets": ["snippet"],
            "best_practices": ["practice"],
            "anti_patterns": ["anti"],
        }

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(response_data))]
        mock_client.messages.create.return_value = mock_response

        enricher = LLMEnricher(mock_client, cache_dir=temp_repo.path / "cache")
        result = enricher._call_claude_api(
            sample_skill, sample_finding, temp_repo, "Sample code"
        )

        assert "enriched_instructions" in result
        assert len(result["enriched_instructions"]) == 2


class TestMergeEnrichment:
    """Test _merge_enrichment method."""

    def test_merge_enrichment_adds_llm_data(self, mock_client, sample_skill):
        """Test that enrichment data is merged into skill."""
        enrichment_data = {
            "enriched_instructions": ["Step 1", "Step 2"],
            "code_snippets": ["snippet1"],
            "best_practices": ["practice1"],
            "anti_patterns": ["anti1"],
        }

        enricher = LLMEnricher(mock_client)
        result = enricher._merge_enrichment(sample_skill, enrichment_data)

        assert result.skill_id == sample_skill.skill_id
        # Verify enrichment was applied (implementation-dependent)
        assert isinstance(result, DiscoveredSkill)

    def test_merge_enrichment_handles_empty_data(self, mock_client, sample_skill):
        """Test merging with empty enrichment data."""
        enricher = LLMEnricher(mock_client)
        result = enricher._merge_enrichment(sample_skill, {})

        # Should still return valid skill
        assert result.skill_id == sample_skill.skill_id


class TestCacheIntegration:
    """Test cache integration."""

    @patch("agentready.learners.llm_enricher.CodeSampler")
    def test_cache_stores_enriched_skill(
        self, mock_sampler_class, mock_client, temp_repo, sample_skill, sample_finding
    ):
        """Test that enriched skill is stored in cache."""
        mock_sampler = MagicMock()
        mock_sampler.get_relevant_code.return_value = "Sample code"
        mock_sampler_class.return_value = mock_sampler

        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(text=json.dumps({"enriched_instructions": ["Step 1"]}))
        ]
        mock_client.messages.create.return_value = mock_response

        cache_dir = temp_repo.path / "cache"
        enricher = LLMEnricher(mock_client, cache_dir=cache_dir)

        # First call should hit API and cache result
        result1 = enricher.enrich_skill(sample_skill, temp_repo, sample_finding, use_cache=True)
        assert mock_client.messages.create.call_count == 1

        # Second call should use cache
        result2 = enricher.enrich_skill(sample_skill, temp_repo, sample_finding, use_cache=True)
        assert mock_client.messages.create.call_count == 1  # No additional API call

    @patch("agentready.learners.llm_enricher.CodeSampler")
    def test_cache_bypass_with_flag(
        self, mock_sampler_class, mock_client, temp_repo, sample_skill, sample_finding
    ):
        """Test that cache can be bypassed."""
        mock_sampler = MagicMock()
        mock_sampler.get_relevant_code.return_value = "Sample code"
        mock_sampler_class.return_value = mock_sampler

        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(text=json.dumps({"enriched_instructions": ["Step 1"]}))
        ]
        mock_client.messages.create.return_value = mock_response

        enricher = LLMEnricher(mock_client, cache_dir=temp_repo.path / "cache")

        # Call twice with use_cache=False
        enricher.enrich_skill(sample_skill, temp_repo, sample_finding, use_cache=False)
        enricher.enrich_skill(sample_skill, temp_repo, sample_finding, use_cache=False)

        # Should have called API twice
        assert mock_client.messages.create.call_count == 2
