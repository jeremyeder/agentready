"""Comprehensive tests for repomix CLI command."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from agentready.cli.repomix import repomix_generate


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


class TestRepomixCLI:
    """Test repomix command CLI interface."""

    def test_repomix_help(self, runner):
        """Test repomix command help."""
        result = runner.invoke(repomix_generate, ["--help"])
        assert result.exit_code == 0
        assert "Generate Repomix repository context" in result.output

    def test_repomix_not_a_git_repo(self, runner):
        """Test repomix fails when not in a git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(repomix_generate, [tmpdir])
            assert result.exit_code == 1
            assert "Not a git repository" in result.output

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_init(self, mock_service_class, runner, temp_git_repo):
        """Test repomix init creates configuration."""
        mock_service = MagicMock()
        mock_service.is_installed.return_value = True
        mock_service.generate_config.return_value = True
        mock_service.generate_ignore.return_value = True
        mock_service.config_path.name = "repomix.config.json"
        mock_service.ignore_path.name = ".repomixignore"
        mock_service_class.return_value = mock_service

        result = runner.invoke(repomix_generate, [str(temp_git_repo), "--init"])

        assert result.exit_code == 0
        assert "Initializing Repomix Configuration" in result.output
        assert "Created repomix.config.json" in result.output
        assert "Created .repomixignore" in result.output
        mock_service.generate_config.assert_called_once_with(overwrite=False)
        mock_service.generate_ignore.assert_called_once_with(overwrite=False)

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_init_repomix_not_installed(
        self, mock_service_class, runner, temp_git_repo
    ):
        """Test repomix init warns when repomix is not installed."""
        mock_service = MagicMock()
        mock_service.is_installed.return_value = False
        mock_service.generate_config.return_value = True
        mock_service.generate_ignore.return_value = True
        mock_service.config_path.name = "repomix.config.json"
        mock_service.ignore_path.name = ".repomixignore"
        mock_service_class.return_value = mock_service

        result = runner.invoke(repomix_generate, [str(temp_git_repo), "--init"])

        assert result.exit_code == 0
        assert "Repomix is not installed" in result.output
        assert "npm install -g repomix" in result.output
        assert "Configuration files will still be created" in result.output

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_init_files_already_exist(
        self, mock_service_class, runner, temp_git_repo
    ):
        """Test repomix init skips existing files."""
        mock_service = MagicMock()
        mock_service.is_installed.return_value = True
        mock_service.generate_config.return_value = False  # Already exists
        mock_service.generate_ignore.return_value = False  # Already exists
        mock_service.config_path.name = "repomix.config.json"
        mock_service.ignore_path.name = ".repomixignore"
        mock_service_class.return_value = mock_service

        result = runner.invoke(repomix_generate, [str(temp_git_repo), "--init"])

        assert result.exit_code == 0
        assert "already exists (skipped)" in result.output

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_check_fresh(self, mock_service_class, runner, temp_git_repo):
        """Test repomix check when output is fresh."""
        mock_output_file = MagicMock()
        mock_output_file.name = "repomix-output.md"

        mock_service = MagicMock()
        mock_service.has_config.return_value = True
        mock_service.check_freshness.return_value = (True, "Output is fresh")
        mock_service.get_output_files.return_value = [mock_output_file]
        mock_service_class.return_value = mock_service

        result = runner.invoke(repomix_generate, [str(temp_git_repo), "--check"])

        assert result.exit_code == 0
        assert "Output is fresh" in result.output
        assert "repomix-output.md" in result.output

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_check_stale(self, mock_service_class, runner, temp_git_repo):
        """Test repomix check when output is stale."""
        mock_service = MagicMock()
        mock_service.has_config.return_value = True
        mock_service.check_freshness.return_value = (False, "Output is stale")
        mock_service_class.return_value = mock_service

        result = runner.invoke(repomix_generate, [str(temp_git_repo), "--check"])

        assert result.exit_code == 1
        assert "Output is stale" in result.output

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_check_not_configured(self, mock_service_class, runner, temp_git_repo):
        """Test repomix check fails when not configured."""
        mock_service = MagicMock()
        mock_service.has_config.return_value = False
        mock_service_class.return_value = mock_service

        result = runner.invoke(repomix_generate, [str(temp_git_repo), "--check"])

        assert result.exit_code == 1
        assert "Repomix not configured" in result.output

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_check_with_custom_max_age(
        self, mock_service_class, runner, temp_git_repo
    ):
        """Test repomix check with custom max age."""
        mock_service = MagicMock()
        mock_service.has_config.return_value = True
        mock_service.check_freshness.return_value = (True, "Output is fresh")
        mock_service.get_output_files.return_value = []
        mock_service_class.return_value = mock_service

        result = runner.invoke(
            repomix_generate, [str(temp_git_repo), "--check", "--max-age", "14"]
        )

        assert result.exit_code == 0
        mock_service.check_freshness.assert_called_with(max_age_days=14)

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_generate_not_configured(self, mock_service_class, runner, temp_git_repo):
        """Test repomix generate fails when not configured."""
        mock_service = MagicMock()
        mock_service.has_config.return_value = False
        mock_service_class.return_value = mock_service

        result = runner.invoke(repomix_generate, [str(temp_git_repo)])

        assert result.exit_code == 1
        assert "Repomix not configured" in result.output

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_generate_not_installed(self, mock_service_class, runner, temp_git_repo):
        """Test repomix generate fails when repomix not installed."""
        mock_service = MagicMock()
        mock_service.has_config.return_value = True
        mock_service.is_installed.return_value = False
        mock_service_class.return_value = mock_service

        result = runner.invoke(repomix_generate, [str(temp_git_repo)])

        assert result.exit_code == 1
        assert "Repomix is not installed" in result.output

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_generate_success(self, mock_service_class, runner, temp_git_repo):
        """Test repomix generate succeeds."""
        mock_service = MagicMock()
        mock_service.has_config.return_value = True
        mock_service.is_installed.return_value = True
        mock_service.run_repomix.return_value = (True, "Generated successfully")
        mock_service.check_freshness.return_value = (True, "Output is fresh")
        mock_service_class.return_value = mock_service

        result = runner.invoke(repomix_generate, [str(temp_git_repo)])

        assert result.exit_code == 0
        assert "Generated successfully" in result.output
        assert "Output is fresh" in result.output
        mock_service.run_repomix.assert_called_once_with(output_format="markdown", verbose=False)

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_generate_failure(self, mock_service_class, runner, temp_git_repo):
        """Test repomix generate handles failures."""
        mock_service = MagicMock()
        mock_service.has_config.return_value = True
        mock_service.is_installed.return_value = True
        mock_service.run_repomix.return_value = (False, "Generation failed")
        mock_service_class.return_value = mock_service

        result = runner.invoke(repomix_generate, [str(temp_git_repo)])

        assert result.exit_code == 1
        assert "Generation failed" in result.output

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_generate_with_xml_format(
        self, mock_service_class, runner, temp_git_repo
    ):
        """Test repomix generate with XML format."""
        mock_service = MagicMock()
        mock_service.has_config.return_value = True
        mock_service.is_installed.return_value = True
        mock_service.run_repomix.return_value = (True, "Generated successfully")
        mock_service.check_freshness.return_value = (True, "Output is fresh")
        mock_service_class.return_value = mock_service

        result = runner.invoke(repomix_generate, [str(temp_git_repo), "--format", "xml"])

        assert result.exit_code == 0
        mock_service.run_repomix.assert_called_once_with(output_format="xml", verbose=False)

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_generate_with_json_format(
        self, mock_service_class, runner, temp_git_repo
    ):
        """Test repomix generate with JSON format."""
        mock_service = MagicMock()
        mock_service.has_config.return_value = True
        mock_service.is_installed.return_value = True
        mock_service.run_repomix.return_value = (True, "Generated successfully")
        mock_service.check_freshness.return_value = (True, "Output is fresh")
        mock_service_class.return_value = mock_service

        result = runner.invoke(repomix_generate, [str(temp_git_repo), "--format", "json"])

        assert result.exit_code == 0
        mock_service.run_repomix.assert_called_once_with(output_format="json", verbose=False)

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_generate_with_plain_format(
        self, mock_service_class, runner, temp_git_repo
    ):
        """Test repomix generate with plain text format."""
        mock_service = MagicMock()
        mock_service.has_config.return_value = True
        mock_service.is_installed.return_value = True
        mock_service.run_repomix.return_value = (True, "Generated successfully")
        mock_service.check_freshness.return_value = (True, "Output is fresh")
        mock_service_class.return_value = mock_service

        result = runner.invoke(repomix_generate, [str(temp_git_repo), "--format", "plain"])

        assert result.exit_code == 0
        mock_service.run_repomix.assert_called_once_with(output_format="plain", verbose=False)

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_generate_verbose(self, mock_service_class, runner, temp_git_repo):
        """Test repomix generate with verbose output."""
        mock_service = MagicMock()
        mock_service.has_config.return_value = True
        mock_service.is_installed.return_value = True
        mock_service.run_repomix.return_value = (True, "Generated successfully")
        mock_service.check_freshness.return_value = (True, "Output is fresh")
        mock_service_class.return_value = mock_service

        result = runner.invoke(repomix_generate, [str(temp_git_repo), "--verbose"])

        assert result.exit_code == 0
        assert "Generating Repomix Repository Context" in result.output
        assert "Repository:" in result.output
        assert "Format:" in result.output
        mock_service.run_repomix.assert_called_once_with(output_format="markdown", verbose=True)

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_generate_default_repository_path(self, mock_service_class, runner):
        """Test repomix defaults to current directory."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        # Call repomix without explicit path
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()
            with runner.isolated_filesystem(temp_dir=tmpdir):
                mock_service.has_config.return_value = False
                result = runner.invoke(repomix_generate)

        # Should use current directory
        assert result.exit_code == 1

    @patch("agentready.cli.repomix.RepomixService")
    def test_repomix_all_formats(self, mock_service_class, runner, temp_git_repo):
        """Test all supported formats."""
        formats = ["markdown", "xml", "json", "plain"]

        for fmt in formats:
            mock_service = MagicMock()
            mock_service.has_config.return_value = True
            mock_service.is_installed.return_value = True
            mock_service.run_repomix.return_value = (True, "Generated successfully")
            mock_service.check_freshness.return_value = (True, "Output is fresh")
            mock_service_class.return_value = mock_service

            result = runner.invoke(repomix_generate, [str(temp_git_repo), "--format", fmt])

            assert result.exit_code == 0
            mock_service.run_repomix.assert_called_with(output_format=fmt, verbose=False)
