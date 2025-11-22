"""Comprehensive tests for learn CLI command."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from agentready.cli.learn import learn


@pytest.fixture
def runner():
    """Create Click test runner."""
    return CliRunner()


@pytest.fixture
def temp_repo_with_assessment():
    """Create temporary repository with assessment file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        agentready_dir = repo_path / ".agentready"
        agentready_dir.mkdir()

        # Create a valid assessment file
        assessment_data = {
            "version": "1.0.0",
            "timestamp": "2025-01-01T00:00:00Z",
            "repository": {
                "name": "test-repo",
                "url": "https://github.com/test/repo",
                "branch": "main",
                "path": str(repo_path),
            },
            "overall_score": 75.0,
            "certification_level": "Gold",
            "findings": [
                {
                    "attribute_id": "claude_md_file",
                    "status": "pass",
                    "score": 100.0,
                    "evidence": ["CLAUDE.md found"],
                    "remediation_steps": [],
                }
            ],
        }

        assessment_file = agentready_dir / "assessment-20250101-000000.json"
        with open(assessment_file, "w") as f:
            json.dump(assessment_data, f)

        yield repo_path


class TestLearnCLI:
    """Test learn command CLI interface."""

    def test_learn_help(self, runner):
        """Test learn command help."""
        result = runner.invoke(learn, ["--help"])
        assert result.exit_code == 0
        assert "Extract reusable patterns" in result.output

    def test_learn_no_assessment_directory(self, runner):
        """Test learn fails when .agentready/ doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(learn, [tmpdir])
            assert result.exit_code == 1
            assert "No assessment found" in result.output

    def test_learn_no_assessment_files(self, runner):
        """Test learn fails when no assessment files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            (repo_path / ".agentready").mkdir()
            result = runner.invoke(learn, [tmpdir])
            assert result.exit_code == 1
            assert "No assessment files found" in result.output

    def test_learn_repository_not_found(self, runner):
        """Test learn fails when repository doesn't exist."""
        result = runner.invoke(learn, ["/nonexistent/path"])
        assert result.exit_code == 1
        assert "Repository not found" in result.output

    @patch("agentready.cli.learn.LearningService")
    def test_learn_json_output(self, mock_service_class, runner, temp_repo_with_assessment):
        """Test learn with JSON output format."""
        # Mock learning service
        mock_service = MagicMock()
        mock_service.run_full_workflow.return_value = {
            "skills_discovered": 2,
            "generated_files": [".skills-proposals/discovered-skills.json"],
            "skills": [],
        }
        mock_service_class.return_value = mock_service

        result = runner.invoke(
            learn, [str(temp_repo_with_assessment), "--output-format", "json"]
        )

        assert result.exit_code == 0
        assert "Discovered 2 skill(s)" in result.output
        mock_service.run_full_workflow.assert_called_once()

    @patch("agentready.cli.learn.LearningService")
    def test_learn_skill_md_output(self, mock_service_class, runner, temp_repo_with_assessment):
        """Test learn with SKILL.md output format."""
        mock_service = MagicMock()
        mock_service.run_full_workflow.return_value = {
            "skills_discovered": 3,
            "generated_files": [".skills-proposals/skill-claude-md.md"],
            "skills": [],
        }
        mock_service_class.return_value = mock_service

        result = runner.invoke(
            learn, [str(temp_repo_with_assessment), "--output-format", "skill_md"]
        )

        assert result.exit_code == 0
        assert "Discovered 3 skill(s)" in result.output
        assert "Review generated SKILL.md files" in result.output

    @patch("agentready.cli.learn.LearningService")
    def test_learn_github_issues_output(
        self, mock_service_class, runner, temp_repo_with_assessment
    ):
        """Test learn with GitHub issues output format."""
        mock_service = MagicMock()
        mock_service.run_full_workflow.return_value = {
            "skills_discovered": 1,
            "generated_files": [".skills-proposals/skill-claude-md-issue.md"],
            "skills": [],
        }
        mock_service_class.return_value = mock_service

        result = runner.invoke(
            learn, [str(temp_repo_with_assessment), "--output-format", "github_issues"]
        )

        assert result.exit_code == 0
        assert "Discovered 1 skill(s)" in result.output
        assert "gh issue create" in result.output

    @patch("agentready.cli.learn.LearningService")
    def test_learn_all_formats(self, mock_service_class, runner, temp_repo_with_assessment):
        """Test learn with 'all' output format."""
        mock_service = MagicMock()
        mock_service.run_full_workflow.return_value = {
            "skills_discovered": 2,
            "generated_files": [
                ".skills-proposals/discovered-skills.json",
                ".skills-proposals/skill-claude-md.md",
            ],
            "skills": [],
        }
        mock_service_class.return_value = mock_service

        result = runner.invoke(
            learn, [str(temp_repo_with_assessment), "--output-format", "all"]
        )

        assert result.exit_code == 0
        assert "Discovered 2 skill(s)" in result.output

    @patch("agentready.cli.learn.LearningService")
    def test_learn_no_skills_found(self, mock_service_class, runner, temp_repo_with_assessment):
        """Test learn when no skills meet confidence threshold."""
        mock_service = MagicMock()
        mock_service.run_full_workflow.return_value = {
            "skills_discovered": 0,
            "generated_files": [],
            "skills": [],
        }
        mock_service_class.return_value = mock_service

        result = runner.invoke(learn, [str(temp_repo_with_assessment)])

        assert result.exit_code == 0
        assert "No skills met the confidence threshold" in result.output
        assert "Try lowering --min-confidence" in result.output

    @patch("agentready.cli.learn.LearningService")
    def test_learn_with_attribute_filter(
        self, mock_service_class, runner, temp_repo_with_assessment
    ):
        """Test learn with specific attribute filter."""
        mock_service = MagicMock()
        mock_service.run_full_workflow.return_value = {
            "skills_discovered": 1,
            "generated_files": [".skills-proposals/discovered-skills.json"],
            "skills": [],
        }
        mock_service_class.return_value = mock_service

        result = runner.invoke(
            learn,
            [
                str(temp_repo_with_assessment),
                "--attribute",
                "claude_md_file",
                "--attribute",
                "type_annotations",
            ],
        )

        assert result.exit_code == 0
        assert "claude_md_file" in result.output
        mock_service.run_full_workflow.assert_called_once()
        call_kwargs = mock_service.run_full_workflow.call_args[1]
        assert call_kwargs["attribute_ids"] == ["claude_md_file", "type_annotations"]

    @patch("agentready.cli.learn.LearningService")
    def test_learn_with_custom_min_confidence(
        self, mock_service_class, runner, temp_repo_with_assessment
    ):
        """Test learn with custom minimum confidence."""
        mock_service = MagicMock()
        mock_service.run_full_workflow.return_value = {
            "skills_discovered": 2,
            "generated_files": [".skills-proposals/discovered-skills.json"],
            "skills": [],
        }
        mock_service_class.return_value = mock_service

        result = runner.invoke(
            learn, [str(temp_repo_with_assessment), "--min-confidence", "85"]
        )

        assert result.exit_code == 0
        mock_service_class.assert_called_with(min_confidence=85, output_dir=".skills-proposals")

    @patch("agentready.cli.learn.LearningService")
    def test_learn_with_custom_output_dir(
        self, mock_service_class, runner, temp_repo_with_assessment
    ):
        """Test learn with custom output directory."""
        mock_service = MagicMock()
        mock_service.run_full_workflow.return_value = {
            "skills_discovered": 1,
            "generated_files": ["custom-dir/discovered-skills.json"],
            "skills": [],
        }
        mock_service_class.return_value = mock_service

        result = runner.invoke(
            learn, [str(temp_repo_with_assessment), "--output-dir", "custom-dir"]
        )

        assert result.exit_code == 0
        mock_service_class.assert_called_with(min_confidence=70, output_dir="custom-dir")

    @patch("agentready.cli.learn.LearningService")
    def test_learn_verbose_mode(self, mock_service_class, runner, temp_repo_with_assessment):
        """Test learn with verbose output."""
        from agentready.models import DiscoveredSkill

        mock_skill = DiscoveredSkill(
            skill_id="test-skill",
            name="Test Skill",
            confidence=85.0,
            pattern_summary="Test pattern summary",
            source_attribute_id="claude_md_file",
            impact_score=10.0,
            reusability_score=80.0,
            implementation_pattern="Test implementation",
            evidence=[],
            extracted_at="2025-01-01T00:00:00Z",
        )

        mock_service = MagicMock()
        mock_service.run_full_workflow.return_value = {
            "skills_discovered": 1,
            "generated_files": [".skills-proposals/discovered-skills.json"],
            "skills": [mock_skill],
        }
        mock_service_class.return_value = mock_service

        result = runner.invoke(learn, [str(temp_repo_with_assessment), "--verbose"])

        assert result.exit_code == 0
        assert "Test Skill" in result.output
        assert "Confidence: 85.0%" in result.output
        assert "Test pattern summary" in result.output

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-key"})
    @patch("agentready.cli.learn.LearningService")
    def test_learn_with_llm_enabled(
        self, mock_service_class, runner, temp_repo_with_assessment
    ):
        """Test learn with LLM enrichment enabled."""
        mock_service = MagicMock()
        mock_service.run_full_workflow.return_value = {
            "skills_discovered": 3,
            "generated_files": [".skills-proposals/discovered-skills.json"],
            "skills": [],
        }
        mock_service_class.return_value = mock_service

        result = runner.invoke(
            learn, [str(temp_repo_with_assessment), "--enable-llm", "--llm-budget", "3"]
        )

        assert result.exit_code == 0
        assert "LLM enrichment: ENABLED" in result.output
        assert "budget: 3 skills" in result.output
        assert "LLM-enriched 3 skill(s)" in result.output

    @patch.dict(os.environ, {}, clear=True)
    @patch("agentready.cli.learn.LearningService")
    def test_learn_llm_no_api_key(self, mock_service_class, runner, temp_repo_with_assessment):
        """Test learn with LLM enabled but no API key."""
        mock_service = MagicMock()
        mock_service.run_full_workflow.return_value = {
            "skills_discovered": 2,
            "generated_files": [".skills-proposals/discovered-skills.json"],
            "skills": [],
        }
        mock_service_class.return_value = mock_service

        result = runner.invoke(learn, [str(temp_repo_with_assessment), "--enable-llm"])

        assert result.exit_code == 0
        assert "ANTHROPIC_API_KEY not set" in result.output
        # Should fall back to non-LLM mode
        call_kwargs = mock_service.run_full_workflow.call_args[1]
        assert call_kwargs["enable_llm"] is False

    @patch("agentready.cli.learn.LearningService")
    def test_learn_with_llm_no_cache(
        self, mock_service_class, runner, temp_repo_with_assessment
    ):
        """Test learn with LLM cache disabled."""
        mock_service = MagicMock()
        mock_service.run_full_workflow.return_value = {
            "skills_discovered": 1,
            "generated_files": [".skills-proposals/discovered-skills.json"],
            "skills": [],
        }
        mock_service_class.return_value = mock_service

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            result = runner.invoke(
                learn, [str(temp_repo_with_assessment), "--enable-llm", "--llm-no-cache"]
            )

        assert result.exit_code == 0
        assert "LLM cache: DISABLED" in result.output

    @patch("agentready.cli.learn.LearningService")
    def test_learn_service_exception(self, mock_service_class, runner, temp_repo_with_assessment):
        """Test learn handles service exceptions gracefully."""
        mock_service = MagicMock()
        mock_service.run_full_workflow.side_effect = Exception("Test error")
        mock_service_class.return_value = mock_service

        result = runner.invoke(learn, [str(temp_repo_with_assessment)])

        assert result.exit_code == 1
        assert "Error during learning" in result.output

    @patch("agentready.cli.learn.LearningService")
    def test_learn_service_exception_verbose(
        self, mock_service_class, runner, temp_repo_with_assessment
    ):
        """Test learn shows traceback in verbose mode on error."""
        mock_service = MagicMock()
        mock_service.run_full_workflow.side_effect = ValueError("Test error")
        mock_service_class.return_value = mock_service

        result = runner.invoke(learn, [str(temp_repo_with_assessment), "--verbose"])

        assert result.exit_code == 1
        assert "Error during learning" in result.output
        # Traceback should be printed in verbose mode

    @patch("agentready.cli.learn.LearningService")
    def test_learn_default_repository_path(self, mock_service_class, runner, temp_repo_with_assessment):
        """Test learn defaults to current directory."""
        mock_service = MagicMock()
        mock_service.run_full_workflow.return_value = {
            "skills_discovered": 1,
            "generated_files": [".skills-proposals/discovered-skills.json"],
            "skills": [],
        }
        mock_service_class.return_value = mock_service

        # Change to temp directory and invoke without path argument
        with runner.isolated_filesystem(temp_dir=str(temp_repo_with_assessment)):
            # Create .agentready with assessment in current dir
            agentready_dir = Path(".agentready")
            agentready_dir.mkdir(exist_ok=True)

            assessment_data = {
                "version": "1.0.0",
                "timestamp": "2025-01-01T00:00:00Z",
                "repository": {"name": "test", "path": "."},
                "overall_score": 75.0,
                "findings": [],
            }

            with open(agentready_dir / "assessment-20250101-000000.json", "w") as f:
                json.dump(assessment_data, f)

            result = runner.invoke(learn)

        assert result.exit_code == 0
