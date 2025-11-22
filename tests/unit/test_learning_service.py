"""Comprehensive tests for learning_service module."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentready.models import DiscoveredSkill
from agentready.services.learning_service import LearningService


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_assessment_file(temp_dir):
    """Create sample assessment file for testing."""
    assessment_data = {
        "version": "1.0.0",
        "timestamp": "2025-01-01T00:00:00",
        "repository": {
            "name": "test-repo",
            "path": str(temp_dir),
            "url": "https://github.com/test/repo",
            "branch": "main",
            "commit_hash": "abc123",
            "languages": {"python": 0.9, "markdown": 0.1},
            "total_files": 100,
            "total_lines": 5000,
        },
        "overall_score": 85.0,
        "certification_level": "Gold",
        "attributes_assessed": 10,
        "attributes_skipped": 5,
        "attributes_total": 15,
        "duration_seconds": 10.5,
        "findings": [
            {
                "attribute": {
                    "id": "claude_md_file",
                    "name": "CLAUDE.md File",
                    "category": "Documentation",
                    "tier": 1,
                    "description": "Repository has CLAUDE.md file",
                    "criteria": "CLAUDE.md exists",
                    "default_weight": 1.0,
                },
                "status": "pass",
                "score": 100.0,
                "measured_value": None,
                "threshold": None,
                "evidence": ["CLAUDE.md found at root"],
                "error_message": None,
            },
            {
                "attribute": {
                    "id": "type_annotations",
                    "name": "Type Annotations",
                    "category": "Code Quality",
                    "tier": 2,
                    "description": "Code uses type annotations",
                    "criteria": ">80% coverage",
                    "default_weight": 0.8,
                },
                "status": "pass",
                "score": 90.0,
                "measured_value": 0.9,
                "threshold": 0.8,
                "evidence": ["90% of functions have type hints"],
                "error_message": None,
            },
        ],
    }

    assessment_file = temp_dir / ".agentready" / "assessment-20250101-000000.json"
    assessment_file.parent.mkdir(parents=True, exist_ok=True)

    with open(assessment_file, "w") as f:
        json.dump(assessment_data, f)

    return assessment_file


@pytest.fixture
def sample_skill():
    """Create sample discovered skill for testing."""
    return DiscoveredSkill(
        skill_id="test-skill",
        name="Test Skill",
        confidence=85.0,
        pattern_summary="Test pattern summary",
        source_attribute_id="claude_md_file",
        impact_score=10.0,
        reusability_score=80.0,
        implementation_pattern="Test implementation",
        evidence=["Evidence 1", "Evidence 2"],
        extracted_at=datetime.now().isoformat(),
    )


class TestLearningServiceInit:
    """Test LearningService initialization."""

    def test_init_defaults(self):
        """Test initialization with default values."""
        service = LearningService()
        assert service.min_confidence == 70.0
        assert service.output_dir == Path(".skills-proposals")

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        service = LearningService(min_confidence=85.0, output_dir="custom-dir")
        assert service.min_confidence == 85.0
        assert service.output_dir == Path("custom-dir")

    def test_init_path_conversion(self):
        """Test that string output_dir is converted to Path."""
        service = LearningService(output_dir="test-dir")
        assert isinstance(service.output_dir, Path)


class TestLoadAssessment:
    """Test load_assessment method."""

    def test_load_valid_assessment(self, temp_dir):
        """Test loading valid assessment file."""
        service = LearningService()

        # Create valid assessment
        assessment_data = {
            "version": "1.0.0",
            "timestamp": "2025-01-01T00:00:00",
            "repository": {"name": "test", "path": str(temp_dir)},
            "overall_score": 75.0,
            "findings": [],
        }

        assessment_file = temp_dir / "assessment.json"
        with open(assessment_file, "w") as f:
            json.dump(assessment_data, f)

        result = service.load_assessment(assessment_file)
        assert result["version"] == "1.0.0"
        assert result["overall_score"] == 75.0

    def test_load_nonexistent_file(self, temp_dir):
        """Test loading nonexistent file raises FileNotFoundError."""
        service = LearningService()
        nonexistent = temp_dir / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            service.load_assessment(nonexistent)

    def test_load_invalid_json(self, temp_dir):
        """Test loading invalid JSON raises ValueError."""
        service = LearningService()

        invalid_file = temp_dir / "invalid.json"
        invalid_file.write_text("not valid json {[")

        with pytest.raises(ValueError, match="Invalid JSON"):
            service.load_assessment(invalid_file)


class TestExtractPatternsFromFile:
    """Test extract_patterns_from_file method."""

    @patch("agentready.services.learning_service.PatternExtractor")
    def test_extract_all_patterns(self, mock_extractor_class, sample_assessment_file, sample_skill):
        """Test extracting all patterns from assessment."""
        # Mock pattern extractor
        mock_extractor = MagicMock()
        mock_extractor.extract_all_patterns.return_value = [sample_skill]
        mock_extractor_class.return_value = mock_extractor

        service = LearningService(min_confidence=70.0)
        skills = service.extract_patterns_from_file(sample_assessment_file)

        assert len(skills) == 1
        assert skills[0].skill_id == "test-skill"
        mock_extractor.extract_all_patterns.assert_called_once()

    @patch("agentready.services.learning_service.PatternExtractor")
    def test_extract_specific_attributes(
        self, mock_extractor_class, sample_assessment_file, sample_skill
    ):
        """Test extracting patterns for specific attributes."""
        mock_extractor = MagicMock()
        mock_extractor.extract_specific_patterns.return_value = [sample_skill]
        mock_extractor_class.return_value = mock_extractor

        service = LearningService(min_confidence=70.0)
        skills = service.extract_patterns_from_file(
            sample_assessment_file, attribute_ids=["claude_md_file"]
        )

        assert len(skills) == 1
        mock_extractor.extract_specific_patterns.assert_called_once_with(["claude_md_file"])

    @patch("agentready.services.learning_service.PatternExtractor")
    def test_filter_by_confidence(self, mock_extractor_class, sample_assessment_file):
        """Test that skills below confidence threshold are filtered out."""
        low_conf_skill = DiscoveredSkill(
            skill_id="low-conf",
            name="Low Confidence Skill",
            confidence=50.0,  # Below threshold
            pattern_summary="Test",
            source_attribute_id="test",
            impact_score=5.0,
            reusability_score=60.0,
            implementation_pattern="Test",
            evidence=[],
            extracted_at=datetime.now().isoformat(),
        )

        high_conf_skill = DiscoveredSkill(
            skill_id="high-conf",
            name="High Confidence Skill",
            confidence=85.0,  # Above threshold
            pattern_summary="Test",
            source_attribute_id="test",
            impact_score=10.0,
            reusability_score=80.0,
            implementation_pattern="Test",
            evidence=[],
            extracted_at=datetime.now().isoformat(),
        )

        mock_extractor = MagicMock()
        mock_extractor.extract_all_patterns.return_value = [low_conf_skill, high_conf_skill]
        mock_extractor_class.return_value = mock_extractor

        service = LearningService(min_confidence=70.0)
        skills = service.extract_patterns_from_file(sample_assessment_file)

        # Only high confidence skill should be returned
        assert len(skills) == 1
        assert skills[0].skill_id == "high-conf"

    @patch("agentready.services.learning_service.PatternExtractor")
    @patch("agentready.services.learning_service.LearningService._enrich_with_llm")
    def test_extract_with_llm_enabled(
        self, mock_enrich, mock_extractor_class, sample_assessment_file, sample_skill
    ):
        """Test extraction with LLM enrichment enabled."""
        mock_extractor = MagicMock()
        mock_extractor.extract_all_patterns.return_value = [sample_skill]
        mock_extractor_class.return_value = mock_extractor

        enriched_skill = DiscoveredSkill(
            skill_id="test-skill",
            name="Test Skill (Enriched)",
            confidence=95.0,
            pattern_summary="Enriched summary",
            source_attribute_id="claude_md_file",
            impact_score=15.0,
            reusability_score=90.0,
            implementation_pattern="Enriched implementation",
            evidence=["Enriched evidence"],
            extracted_at=datetime.now().isoformat(),
        )

        mock_enrich.return_value = [enriched_skill]

        service = LearningService(min_confidence=70.0)
        skills = service.extract_patterns_from_file(
            sample_assessment_file, enable_llm=True, llm_budget=5
        )

        assert len(skills) == 1
        assert skills[0].name == "Test Skill (Enriched)"
        mock_enrich.assert_called_once()


class TestGenerateSkills:
    """Test generate_skills method."""

    def test_generate_json_format(self, temp_dir, sample_skill):
        """Test generating JSON format."""
        service = LearningService(output_dir=temp_dir / "output")
        files = service.generate_skills([sample_skill], output_format="json")

        assert len(files) == 1
        assert files[0].name == "discovered-skills.json"
        assert files[0].exists()

        # Verify JSON content
        with open(files[0]) as f:
            data = json.load(f)
            assert data["skill_count"] == 1
            assert len(data["discovered_skills"]) == 1

    @patch("agentready.services.learning_service.SkillGenerator")
    def test_generate_skill_md_format(self, mock_generator_class, temp_dir, sample_skill):
        """Test generating SKILL.md format."""
        mock_generator = MagicMock()
        mock_generator.generate_skill_file.return_value = temp_dir / "skill-test.md"
        mock_generator_class.return_value = mock_generator

        service = LearningService(output_dir=temp_dir)
        service.skill_generator = mock_generator

        files = service.generate_skills([sample_skill], output_format="skill_md")

        assert len(files) == 1
        mock_generator.generate_skill_file.assert_called_once_with(sample_skill)

    @patch("agentready.services.learning_service.SkillGenerator")
    def test_generate_github_issues_format(self, mock_generator_class, temp_dir, sample_skill):
        """Test generating GitHub issues format."""
        mock_generator = MagicMock()
        mock_generator.generate_github_issue.return_value = temp_dir / "issue-test.md"
        mock_generator_class.return_value = mock_generator

        service = LearningService(output_dir=temp_dir)
        service.skill_generator = mock_generator

        files = service.generate_skills([sample_skill], output_format="github_issues")

        assert len(files) == 1
        mock_generator.generate_github_issue.assert_called_once_with(sample_skill)

    @patch("agentready.services.learning_service.SkillGenerator")
    def test_generate_markdown_format(self, mock_generator_class, temp_dir, sample_skill):
        """Test generating markdown report format."""
        mock_generator = MagicMock()
        mock_generator.generate_markdown_report.return_value = temp_dir / "report-test.md"
        mock_generator_class.return_value = mock_generator

        service = LearningService(output_dir=temp_dir)
        service.skill_generator = mock_generator

        files = service.generate_skills([sample_skill], output_format="markdown")

        assert len(files) == 1
        mock_generator.generate_markdown_report.assert_called_once_with(sample_skill)

    @patch("agentready.services.learning_service.SkillGenerator")
    def test_generate_all_formats(self, mock_generator_class, temp_dir, sample_skill):
        """Test generating all formats."""
        mock_generator = MagicMock()
        mock_generator.generate_all_formats.return_value = {
            "skill_md": temp_dir / "skill.md",
            "github_issue": temp_dir / "issue.md",
            "markdown": temp_dir / "report.md",
        }
        mock_generator_class.return_value = mock_generator

        service = LearningService(output_dir=temp_dir)
        service.skill_generator = mock_generator

        files = service.generate_skills([sample_skill], output_format="all")

        # Should include JSON + all other formats
        assert len(files) == 4
        assert any(f.name == "discovered-skills.json" for f in files)
        mock_generator.generate_all_formats.assert_called_once_with(sample_skill)


class TestGenerateJson:
    """Test _generate_json private method."""

    def test_generate_json_creates_directory(self, temp_dir, sample_skill):
        """Test that _generate_json creates output directory."""
        output_dir = temp_dir / "nested" / "output"
        service = LearningService(output_dir=output_dir)

        json_file = service._generate_json([sample_skill])

        assert output_dir.exists()
        assert json_file.exists()

    def test_generate_json_content(self, temp_dir, sample_skill):
        """Test JSON content structure."""
        service = LearningService(output_dir=temp_dir)
        json_file = service._generate_json([sample_skill])

        with open(json_file) as f:
            data = json.load(f)

        assert "generated_at" in data
        assert data["skill_count"] == 1
        assert data["min_confidence"] == 70.0
        assert len(data["discovered_skills"]) == 1
        assert data["discovered_skills"][0]["skill_id"] == "test-skill"


class TestEnrichWithLLM:
    """Test _enrich_with_llm private method."""

    @patch.dict("os.environ", {}, clear=True)
    def test_enrich_no_api_key(self, sample_assessment_file, sample_skill):
        """Test enrichment fails gracefully without API key."""
        service = LearningService()

        # Create mock assessment
        from agentready.models import Assessment, Repository

        repo = Repository(path=Path("."), languages={}, total_files=0, total_lines=0)
        assessment = Assessment(
            repository=repo,
            timestamp=datetime.now(),
            overall_score=75.0,
            certification_level="Gold",
            attributes_assessed=1,
            attributes_not_assessed=0,
            attributes_total=1,
            findings=[],
            config=None,
            duration_seconds=1.0,
        )

        result = service._enrich_with_llm([sample_skill], assessment, budget=5)

        # Should return original skills unchanged
        assert len(result) == 1
        assert result[0].skill_id == sample_skill.skill_id

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"})
    @patch("agentready.services.learning_service.Anthropic")
    @patch("agentready.services.learning_service.LLMEnricher")
    def test_enrich_with_api_key(self, mock_enricher_class, mock_anthropic, sample_skill):
        """Test enrichment with API key."""
        from agentready.models import Assessment, Attribute, Finding, Repository

        # Create mock enricher
        enriched_skill = DiscoveredSkill(
            skill_id="test-skill",
            name="Test Skill (Enriched)",
            confidence=95.0,
            pattern_summary="Enriched",
            source_attribute_id="claude_md_file",
            impact_score=15.0,
            reusability_score=90.0,
            implementation_pattern="Enriched",
            evidence=[],
            extracted_at=datetime.now().isoformat(),
        )

        mock_enricher = MagicMock()
        mock_enricher.enrich_skill.return_value = enriched_skill
        mock_enricher_class.return_value = mock_enricher

        # Create mock assessment with finding
        repo = Repository(path=Path("."), languages={}, total_files=0, total_lines=0)
        attribute = Attribute(
            id="claude_md_file",
            name="CLAUDE.md",
            category="Documentation",
            tier=1,
            description="Test",
            criteria="Test",
        )
        finding = Finding(attribute=attribute, status="pass", score=100.0)

        assessment = Assessment(
            repository=repo,
            timestamp=datetime.now(),
            overall_score=75.0,
            certification_level="Gold",
            attributes_assessed=1,
            attributes_not_assessed=0,
            attributes_total=1,
            findings=[finding],
            config=None,
            duration_seconds=1.0,
        )

        service = LearningService()
        result = service._enrich_with_llm([sample_skill], assessment, budget=5)

        assert len(result) == 1
        assert result[0].name == "Test Skill (Enriched)"
        mock_enricher.enrich_skill.assert_called_once()

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"})
    @patch("agentready.services.learning_service.Anthropic")
    @patch("agentready.services.learning_service.LLMEnricher")
    def test_enrich_respects_budget(self, mock_enricher_class, mock_anthropic, sample_skill):
        """Test that enrichment respects budget limit."""
        from agentready.models import Assessment, Repository

        mock_enricher = MagicMock()
        mock_enricher_class.return_value = mock_enricher

        repo = Repository(path=Path("."), languages={}, total_files=0, total_lines=0)
        assessment = Assessment(
            repository=repo,
            timestamp=datetime.now(),
            overall_score=75.0,
            certification_level="Gold",
            attributes_assessed=1,
            attributes_not_assessed=0,
            attributes_total=1,
            findings=[],
            config=None,
            duration_seconds=1.0,
        )

        # Create 5 skills, budget of 2
        skills = [sample_skill] * 5
        service = LearningService()
        service._enrich_with_llm(skills, assessment, budget=2)

        # Should only enrich 2 skills
        assert mock_enricher.enrich_skill.call_count <= 2


class TestRunFullWorkflow:
    """Test run_full_workflow method."""

    @patch("agentready.services.learning_service.LearningService.extract_patterns_from_file")
    @patch("agentready.services.learning_service.LearningService.generate_skills")
    def test_full_workflow(self, mock_generate, mock_extract, sample_assessment_file, sample_skill, temp_dir):
        """Test complete workflow execution."""
        mock_extract.return_value = [sample_skill]
        mock_generate.return_value = [temp_dir / "discovered-skills.json"]

        service = LearningService(output_dir=temp_dir)
        result = service.run_full_workflow(
            assessment_file=sample_assessment_file,
            output_format="json",
            attribute_ids=None,
            enable_llm=False,
            llm_budget=5,
        )

        assert result["skills_discovered"] == 1
        assert result["min_confidence"] == 70.0
        assert result["output_format"] == "json"
        assert len(result["generated_files"]) == 1
        assert len(result["skills"]) == 1

        mock_extract.assert_called_once()
        mock_generate.assert_called_once_with([sample_skill], "json")


class TestFindFindingForSkill:
    """Test _find_finding_for_skill private method."""

    def test_find_matching_finding(self, sample_skill):
        """Test finding matching Finding for skill."""
        from agentready.models import Assessment, Attribute, Finding, Repository

        repo = Repository(path=Path("."), languages={}, total_files=0, total_lines=0)
        attribute = Attribute(
            id="claude_md_file",
            name="CLAUDE.md",
            category="Documentation",
            tier=1,
            description="Test",
            criteria="Test",
        )
        finding = Finding(attribute=attribute, status="pass", score=100.0)

        assessment = Assessment(
            repository=repo,
            timestamp=datetime.now(),
            overall_score=75.0,
            certification_level="Gold",
            attributes_assessed=1,
            attributes_not_assessed=0,
            attributes_total=1,
            findings=[finding],
            config=None,
            duration_seconds=1.0,
        )

        service = LearningService()
        result = service._find_finding_for_skill(assessment, sample_skill)

        assert result is not None
        assert result.attribute.id == "claude_md_file"

    def test_find_no_matching_finding(self, sample_skill):
        """Test when no matching Finding exists."""
        from agentready.models import Assessment, Repository

        repo = Repository(path=Path("."), languages={}, total_files=0, total_lines=0)
        assessment = Assessment(
            repository=repo,
            timestamp=datetime.now(),
            overall_score=75.0,
            certification_level="Gold",
            attributes_assessed=0,
            attributes_not_assessed=0,
            attributes_total=0,
            findings=[],
            config=None,
            duration_seconds=1.0,
        )

        service = LearningService()
        result = service._find_finding_for_skill(assessment, sample_skill)

        assert result is None
