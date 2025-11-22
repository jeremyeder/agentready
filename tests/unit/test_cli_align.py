"""Comprehensive tests for align CLI command."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from agentready.cli.align import align, get_certification_level


@pytest.fixture
def runner():
    """Create Click test runner."""
    return CliRunner()


@pytest.fixture
def temp_git_repo():
    """Create temporary git repository."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        (repo_path / ".git").mkdir()
        yield repo_path


class TestGetCertificationLevel:
    """Test get_certification_level helper function."""

    def test_platinum_level(self):
        """Test Platinum certification (90-100)."""
        level, emoji = get_certification_level(95.0)
        assert level == "Platinum"
        assert emoji == "💎"

        level, emoji = get_certification_level(90.0)
        assert level == "Platinum"
        assert emoji == "💎"

    def test_gold_level(self):
        """Test Gold certification (75-89)."""
        level, emoji = get_certification_level(80.0)
        assert level == "Gold"
        assert emoji == "🥇"

        level, emoji = get_certification_level(75.0)
        assert level == "Gold"
        assert emoji == "🥇"

    def test_silver_level(self):
        """Test Silver certification (60-74)."""
        level, emoji = get_certification_level(65.0)
        assert level == "Silver"
        assert emoji == "🥈"

        level, emoji = get_certification_level(60.0)
        assert level == "Silver"
        assert emoji == "🥈"

    def test_bronze_level(self):
        """Test Bronze certification (40-59)."""
        level, emoji = get_certification_level(50.0)
        assert level == "Bronze"
        assert emoji == "🥉"

        level, emoji = get_certification_level(40.0)
        assert level == "Bronze"
        assert emoji == "🥉"

    def test_needs_improvement(self):
        """Test Needs Improvement level (<40)."""
        level, emoji = get_certification_level(30.0)
        assert level == "Needs Improvement"
        assert emoji == "📊"

        level, emoji = get_certification_level(0.0)
        assert level == "Needs Improvement"
        assert emoji == "📊"


class TestAlignCLI:
    """Test align command CLI interface."""

    def test_align_help(self, runner):
        """Test align command help."""
        result = runner.invoke(align, ["--help"])
        assert result.exit_code == 0
        assert "Align repository with best practices" in result.output

    def test_align_not_a_git_repo(self, runner):
        """Test align fails when not in a git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(align, [tmpdir])
            assert result.exit_code == 1
            assert "Not a git repository" in result.output

    @patch("agentready.cli.align.LanguageDetector")
    @patch("agentready.cli.align.Scanner")
    @patch("agentready.cli.align.FixerService")
    def test_align_dry_run(
        self, mock_fixer_class, mock_scanner_class, mock_detector_class, runner, temp_git_repo
    ):
        """Test align in dry-run mode."""
        # Mock language detector
        mock_detector = MagicMock()
        mock_detector.detect_languages.return_value = ["python"]
        mock_detector_class.return_value = mock_detector

        # Mock scanner and assessment
        mock_assessment = MagicMock()
        mock_assessment.overall_score = 65.0
        mock_assessment.findings = [
            MagicMock(status="fail", attribute_id="test_attr")
        ]

        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = mock_assessment
        mock_scanner_class.return_value = mock_scanner

        # Mock fixer service
        mock_fix = MagicMock()
        mock_fix.attribute_id = "test_attr"
        mock_fix.description = "Fix test attribute"
        mock_fix.points_gained = 5.0
        mock_fix.preview.return_value = "Preview of changes"

        mock_fix_plan = MagicMock()
        mock_fix_plan.fixes = [mock_fix]
        mock_fix_plan.points_gained = 5.0
        mock_fix_plan.projected_score = 70.0

        mock_fixer = MagicMock()
        mock_fixer.generate_fix_plan.return_value = mock_fix_plan
        mock_fixer_class.return_value = mock_fixer

        result = runner.invoke(align, [str(temp_git_repo), "--dry-run"])

        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "Current Score: 65.0" in result.output
        assert "Projected Score: 70.0" in result.output
        assert "Fix test attribute" in result.output
        assert "Run without --dry-run to apply fixes" in result.output
        # Should not call apply_fixes in dry-run
        mock_fixer.apply_fixes.assert_not_called()

    @patch("agentready.cli.align.LanguageDetector")
    @patch("agentready.cli.align.Scanner")
    @patch("agentready.cli.align.FixerService")
    def test_align_no_fixes_available(
        self, mock_fixer_class, mock_scanner_class, mock_detector_class, runner, temp_git_repo
    ):
        """Test align when no automatic fixes are available."""
        # Mock language detector
        mock_detector = MagicMock()
        mock_detector.detect_languages.return_value = ["python"]
        mock_detector_class.return_value = mock_detector

        # Mock scanner
        mock_assessment = MagicMock()
        mock_assessment.overall_score = 90.0
        mock_assessment.findings = []

        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = mock_assessment
        mock_scanner_class.return_value = mock_scanner

        # Mock fixer service with no fixes
        mock_fix_plan = MagicMock()
        mock_fix_plan.fixes = []

        mock_fixer = MagicMock()
        mock_fixer.generate_fix_plan.return_value = mock_fix_plan
        mock_fixer_class.return_value = mock_fixer

        result = runner.invoke(align, [str(temp_git_repo)])

        assert result.exit_code == 0
        assert "No automatic fixes available" in result.output

    @patch("agentready.cli.align.LanguageDetector")
    @patch("agentready.cli.align.Scanner")
    @patch("agentready.cli.align.FixerService")
    def test_align_apply_fixes_confirmed(
        self, mock_fixer_class, mock_scanner_class, mock_detector_class, runner, temp_git_repo
    ):
        """Test align applies fixes when user confirms."""
        # Mock language detector
        mock_detector = MagicMock()
        mock_detector.detect_languages.return_value = ["python"]
        mock_detector_class.return_value = mock_detector

        # Mock scanner
        mock_assessment = MagicMock()
        mock_assessment.overall_score = 65.0
        mock_assessment.findings = [MagicMock(status="fail")]

        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = mock_assessment
        mock_scanner_class.return_value = mock_scanner

        # Mock fixer service
        mock_fix = MagicMock()
        mock_fix.attribute_id = "test_attr"
        mock_fix.description = "Fix test attribute"
        mock_fix.points_gained = 5.0
        mock_fix.preview.return_value = "Preview"

        mock_fix_plan = MagicMock()
        mock_fix_plan.fixes = [mock_fix]
        mock_fix_plan.points_gained = 5.0
        mock_fix_plan.projected_score = 70.0

        mock_fixer = MagicMock()
        mock_fixer.generate_fix_plan.return_value = mock_fix_plan
        mock_fixer.apply_fixes.return_value = {
            "succeeded": 1,
            "failed": 0,
            "failures": [],
        }
        mock_fixer_class.return_value = mock_fixer

        # Simulate user confirming
        result = runner.invoke(align, [str(temp_git_repo)], input="y\n")

        assert result.exit_code == 0
        assert "Fixes applied: 1/1" in result.output
        mock_fixer.apply_fixes.assert_called_once()

    @patch("agentready.cli.align.LanguageDetector")
    @patch("agentready.cli.align.Scanner")
    @patch("agentready.cli.align.FixerService")
    def test_align_apply_fixes_aborted(
        self, mock_fixer_class, mock_scanner_class, mock_detector_class, runner, temp_git_repo
    ):
        """Test align aborts when user declines."""
        # Mock language detector
        mock_detector = MagicMock()
        mock_detector.detect_languages.return_value = ["python"]
        mock_detector_class.return_value = mock_detector

        # Mock scanner
        mock_assessment = MagicMock()
        mock_assessment.overall_score = 65.0
        mock_assessment.findings = [MagicMock(status="fail")]

        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = mock_assessment
        mock_scanner_class.return_value = mock_scanner

        # Mock fixer service
        mock_fix = MagicMock()
        mock_fix.attribute_id = "test_attr"
        mock_fix.description = "Fix test attribute"
        mock_fix.points_gained = 5.0
        mock_fix.preview.return_value = "Preview"

        mock_fix_plan = MagicMock()
        mock_fix_plan.fixes = [mock_fix]
        mock_fix_plan.points_gained = 5.0
        mock_fix_plan.projected_score = 70.0

        mock_fixer = MagicMock()
        mock_fixer.generate_fix_plan.return_value = mock_fix_plan
        mock_fixer_class.return_value = mock_fixer

        # Simulate user declining
        result = runner.invoke(align, [str(temp_git_repo)], input="n\n")

        assert result.exit_code == 0
        assert "Aborted" in result.output
        mock_fixer.apply_fixes.assert_not_called()

    @patch("agentready.cli.align.LanguageDetector")
    @patch("agentready.cli.align.Scanner")
    @patch("agentready.cli.align.FixerService")
    def test_align_interactive_mode(
        self, mock_fixer_class, mock_scanner_class, mock_detector_class, runner, temp_git_repo
    ):
        """Test align in interactive mode."""
        # Mock language detector
        mock_detector = MagicMock()
        mock_detector.detect_languages.return_value = ["python"]
        mock_detector_class.return_value = mock_detector

        # Mock scanner
        mock_assessment = MagicMock()
        mock_assessment.overall_score = 65.0
        mock_assessment.findings = [MagicMock(status="fail")]

        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = mock_assessment
        mock_scanner_class.return_value = mock_scanner

        # Mock fixer service with 2 fixes
        mock_fix1 = MagicMock()
        mock_fix1.attribute_id = "test_attr1"
        mock_fix1.description = "Fix 1"
        mock_fix1.points_gained = 3.0
        mock_fix1.preview.return_value = "Preview 1"

        mock_fix2 = MagicMock()
        mock_fix2.attribute_id = "test_attr2"
        mock_fix2.description = "Fix 2"
        mock_fix2.points_gained = 2.0
        mock_fix2.preview.return_value = "Preview 2"

        mock_fix_plan = MagicMock()
        mock_fix_plan.fixes = [mock_fix1, mock_fix2]
        mock_fix_plan.points_gained = 5.0
        mock_fix_plan.projected_score = 70.0

        mock_fixer = MagicMock()
        mock_fixer.generate_fix_plan.return_value = mock_fix_plan
        mock_fixer.apply_fixes.return_value = {
            "succeeded": 1,
            "failed": 0,
            "failures": [],
        }
        mock_fixer_class.return_value = mock_fixer

        # Simulate user confirming first fix, declining second
        result = runner.invoke(align, [str(temp_git_repo), "--interactive"], input="y\nn\n")

        assert result.exit_code == 0
        assert "Interactive mode" in result.output
        # Should only apply first fix
        call_args = mock_fixer.apply_fixes.call_args[0][0]
        assert len(call_args) == 1

    @patch("agentready.cli.align.LanguageDetector")
    @patch("agentready.cli.align.Scanner")
    @patch("agentready.cli.align.FixerService")
    def test_align_with_attribute_filter(
        self, mock_fixer_class, mock_scanner_class, mock_detector_class, runner, temp_git_repo
    ):
        """Test align with specific attributes filter."""
        # Mock language detector
        mock_detector = MagicMock()
        mock_detector.detect_languages.return_value = ["python"]
        mock_detector_class.return_value = mock_detector

        # Mock scanner
        mock_assessment = MagicMock()
        mock_assessment.overall_score = 65.0
        mock_assessment.findings = [MagicMock(status="fail")]

        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = mock_assessment
        mock_scanner_class.return_value = mock_scanner

        # Mock fixer service
        mock_fix_plan = MagicMock()
        mock_fix_plan.fixes = []

        mock_fixer = MagicMock()
        mock_fixer.generate_fix_plan.return_value = mock_fix_plan
        mock_fixer_class.return_value = mock_fixer

        result = runner.invoke(
            align, [str(temp_git_repo), "--attributes", "claude_md_file,readme_file"]
        )

        # Should pass attribute list to generate_fix_plan
        call_args = mock_fixer.generate_fix_plan.call_args[0]
        assert call_args[2] == ["claude_md_file", "readme_file"]

    @patch("agentready.cli.align.LanguageDetector")
    @patch("agentready.cli.align.Scanner")
    def test_align_assessment_error(
        self, mock_scanner_class, mock_detector_class, runner, temp_git_repo
    ):
        """Test align handles assessment errors gracefully."""
        # Mock language detector
        mock_detector = MagicMock()
        mock_detector.detect_languages.return_value = ["python"]
        mock_detector_class.return_value = mock_detector

        # Mock scanner to raise exception
        mock_scanner = MagicMock()
        mock_scanner.scan.side_effect = Exception("Assessment failed")
        mock_scanner_class.return_value = mock_scanner

        result = runner.invoke(align, [str(temp_git_repo)])

        assert result.exit_code == 1
        assert "Error during assessment" in result.output

    @patch("agentready.cli.align.LanguageDetector")
    @patch("agentready.cli.align.Scanner")
    @patch("agentready.cli.align.FixerService")
    def test_align_with_failed_fixes(
        self, mock_fixer_class, mock_scanner_class, mock_detector_class, runner, temp_git_repo
    ):
        """Test align reports failures correctly."""
        # Mock language detector
        mock_detector = MagicMock()
        mock_detector.detect_languages.return_value = ["python"]
        mock_detector_class.return_value = mock_detector

        # Mock scanner
        mock_assessment = MagicMock()
        mock_assessment.overall_score = 65.0
        mock_assessment.findings = [MagicMock(status="fail")]

        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = mock_assessment
        mock_scanner_class.return_value = mock_scanner

        # Mock fixer service with some failures
        mock_fix = MagicMock()
        mock_fix.attribute_id = "test_attr"
        mock_fix.description = "Fix test attribute"
        mock_fix.points_gained = 5.0
        mock_fix.preview.return_value = "Preview"

        mock_fix_plan = MagicMock()
        mock_fix_plan.fixes = [mock_fix]
        mock_fix_plan.points_gained = 5.0
        mock_fix_plan.projected_score = 70.0

        mock_fixer = MagicMock()
        mock_fixer.generate_fix_plan.return_value = mock_fix_plan
        mock_fixer.apply_fixes.return_value = {
            "succeeded": 0,
            "failed": 1,
            "failures": ["Fix failed: permission denied"],
        }
        mock_fixer_class.return_value = mock_fixer

        result = runner.invoke(align, [str(temp_git_repo)], input="y\n")

        assert result.exit_code == 0
        assert "Fixes applied: 0/1" in result.output
        assert "Fixes failed: 1" in result.output
        assert "permission denied" in result.output

    @patch("agentready.cli.align.LanguageDetector")
    @patch("agentready.cli.align.Scanner")
    @patch("agentready.cli.align.FixerService")
    def test_align_interactive_no_fixes_selected(
        self, mock_fixer_class, mock_scanner_class, mock_detector_class, runner, temp_git_repo
    ):
        """Test align aborts when no fixes selected in interactive mode."""
        # Mock language detector
        mock_detector = MagicMock()
        mock_detector.detect_languages.return_value = ["python"]
        mock_detector_class.return_value = mock_detector

        # Mock scanner
        mock_assessment = MagicMock()
        mock_assessment.overall_score = 65.0
        mock_assessment.findings = [MagicMock(status="fail")]

        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = mock_assessment
        mock_scanner_class.return_value = mock_scanner

        # Mock fixer service
        mock_fix = MagicMock()
        mock_fix.attribute_id = "test_attr"
        mock_fix.description = "Fix test attribute"
        mock_fix.points_gained = 5.0
        mock_fix.preview.return_value = "Preview"

        mock_fix_plan = MagicMock()
        mock_fix_plan.fixes = [mock_fix]
        mock_fix_plan.points_gained = 5.0
        mock_fix_plan.projected_score = 70.0

        mock_fixer = MagicMock()
        mock_fixer.generate_fix_plan.return_value = mock_fix_plan
        mock_fixer_class.return_value = mock_fixer

        # Simulate user declining all fixes in interactive mode
        result = runner.invoke(align, [str(temp_git_repo), "--interactive"], input="n\n")

        assert result.exit_code == 0
        assert "No fixes selected" in result.output
        mock_fixer.apply_fixes.assert_not_called()
