"""Integration tests for assess CLI command workflows."""

import json
import subprocess
import tempfile
from pathlib import Path

from click.testing import CliRunner

from agentready.cli.main import cli


def init_git_repo(repo_path: Path):
    """Initialize a git repository with an initial commit.

    Args:
        repo_path: Path to repository directory
    """
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    # Create initial commit
    (repo_path / ".gitkeep").write_text("")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )


class TestAssessWorkflow:
    """Test complete assess command workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_assess_generates_all_reports(self):
        """Test assess generates HTML, Markdown, and JSON reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text(
                "# Test Project\n\nDescription here.\n"
            )
            (repo_path / "CLAUDE.md").write_text("# Developer Guide\n")

            result = self.runner.invoke(cli, ["assess", tmpdir])

            assert result.exit_code == 0
            assert "Assessment complete" in result.output

            # Check all report formats were generated
            reports_dir = repo_path / ".agentready"
            assert reports_dir.exists()

            # Should have HTML report
            html_files = list(reports_dir.glob("report-*.html"))
            assert len(html_files) >= 1

            # Should have JSON report
            json_files = list(reports_dir.glob("assessment-*.json"))
            assert len(json_files) >= 1

            # Should have Markdown report
            md_files = list(reports_dir.glob("report-*.md"))
            assert len(md_files) >= 1

    def test_assess_with_custom_output_dir(self):
        """Test assess --output-dir creates reports in custom location."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "repo"
            repo_path.mkdir()
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            custom_output = Path(tmpdir) / "custom_reports"

            result = self.runner.invoke(
                cli, ["assess", str(repo_path), "--output-dir", str(custom_output)]
            )

            assert result.exit_code == 0
            assert custom_output.exists()
            assert len(list(custom_output.glob("*.html"))) >= 1

    def test_assess_with_config_file(self):
        """Test assess --config loads custom configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            # Create custom config
            config_path = Path(tmpdir) / "custom.yml"
            config_path.write_text(
                """
schema_version: "1.0"
tier_weights:
  tier_1: 50
  tier_2: 30
  tier_3: 15
  tier_4: 5
"""
            )

            result = self.runner.invoke(
                cli, ["assess", str(repo_path), "--config", str(config_path)]
            )

            assert result.exit_code == 0

    def test_assess_json_schema_validity(self):
        """Test assess generates valid JSON with required schema fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            result = self.runner.invoke(cli, ["assess", tmpdir])

            assert result.exit_code == 0

            # Read JSON report
            reports_dir = repo_path / ".agentready"
            json_files = list(reports_dir.glob("assessment-*.json"))
            assert len(json_files) >= 1

            json_data = json.loads(json_files[0].read_text())

            # Verify schema fields
            assert "schema_version" in json_data
            assert "timestamp" in json_data
            assert "overall_score" in json_data
            assert "findings" in json_data
            assert isinstance(json_data["findings"], list)

    def test_assess_verbose_output(self):
        """Test assess --verbose provides detailed logging."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            result = self.runner.invoke(cli, ["assess", tmpdir, "--verbose"])

            assert result.exit_code == 0
            # Verbose mode should show more details
            assert "Running assessors" in result.output or "Scanning" in result.output

    def test_assess_exclude_attributes(self):
        """Test assess --exclude filters out specific attributes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            # Use --exclude multiple times (it's defined with multiple=True)
            result = self.runner.invoke(
                cli,
                [
                    "assess",
                    tmpdir,
                    "--exclude",
                    "type_annotations",
                    "--exclude",
                    "test_coverage",
                ],
            )

            assert result.exit_code == 0

            # Read JSON to verify exclusion
            reports_dir = repo_path / ".agentready"
            json_files = list(reports_dir.glob("assessment-*.json"))
            json_data = json.loads(json_files[0].read_text())

            # Excluded attributes should not appear in findings
            attribute_ids = [f["attribute"]["id"] for f in json_data["findings"]]
            assert "type_annotations" not in attribute_ids
            assert "test_coverage" not in attribute_ids

    def test_assess_default_current_directory(self):
        """Test assess defaults to current directory when no path provided."""
        # This test uses the actual AgentReady repo
        result = self.runner.invoke(cli, ["assess"])

        # Should succeed or fail gracefully
        assert result.exit_code in [0, 1]
        if result.exit_code == 0:
            assert "Score:" in result.output or "Assessment complete" in result.output

    def test_assess_non_git_repo_fails(self):
        """Test assess fails gracefully on non-git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            (repo_path / "README.md").write_text("# Test\n")
            # Intentionally no .git directory

            result = self.runner.invoke(cli, ["assess", tmpdir])

            # Should fail with clear error
            assert result.exit_code == 1
            assert "not a git repository" in result.output.lower()

    def test_assess_nonexistent_path_fails(self):
        """Test assess fails on nonexistent path."""
        result = self.runner.invoke(cli, ["assess", "/nonexistent/path/to/repo"])

        assert result.exit_code != 0

    def test_assess_symlink_latest_report(self):
        """Test assess creates 'latest' symlinks to newest reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            result = self.runner.invoke(cli, ["assess", tmpdir])

            assert result.exit_code == 0

            # Check for latest symlinks
            reports_dir = repo_path / ".agentready"
            latest_html = reports_dir / "report-latest.html"
            latest_json = reports_dir / "assessment-latest.json"
            latest_md = reports_dir / "report-latest.md"

            # At least one latest symlink should exist
            assert latest_html.exists() or latest_json.exists() or latest_md.exists()

            # If symlink exists, verify it points to a real file
            if latest_html.exists() and latest_html.is_symlink():
                assert latest_html.resolve().exists()

    def test_assess_help(self):
        """Test assess --help displays usage."""
        result = self.runner.invoke(cli, ["assess", "--help"])

        assert result.exit_code == 0
        assert (
            "Assess a repository" in result.output or "assess" in result.output.lower()
        )
        assert "--verbose" in result.output
        assert "--output-dir" in result.output
        assert "--config" in result.output
        assert "--exclude" in result.output


class TestAssessEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_assess_empty_repository(self):
        """Test assess handles empty repository gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            # No files at all

            result = self.runner.invoke(cli, ["assess", tmpdir])

            # Should complete (possibly with low score)
            assert result.exit_code == 0

    def test_assess_minimal_repository(self):
        """Test assess handles minimal repository with just README."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Minimal\n")

            result = self.runner.invoke(cli, ["assess", tmpdir])

            assert result.exit_code == 0
            assert "Score:" in result.output

    def test_assess_multiple_runs_create_unique_reports(self):
        """Test multiple assess runs create unique timestamped reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            # Run assessment twice
            result1 = self.runner.invoke(cli, ["assess", tmpdir])
            assert result1.exit_code == 0

            # Ensure different second timestamp
            import time

            time.sleep(1.1)  # Need at least 1 second to get different timestamp

            result2 = self.runner.invoke(cli, ["assess", tmpdir])
            assert result2.exit_code == 0

            # Should have multiple timestamped reports
            reports_dir = repo_path / ".agentready"
            json_files = list(reports_dir.glob("assessment-*.json"))

            # Filter out 'latest' symlinks
            timestamped_files = [f for f in json_files if "latest" not in f.name]

            # Should have at least 2 unique reports
            assert len(timestamped_files) >= 2

    def test_assess_invalid_config_file(self):
        """Test assess handles invalid config file gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            # Create invalid YAML config
            config_path = Path(tmpdir) / "invalid.yml"
            config_path.write_text("invalid: yaml: content: [[[")

            result = self.runner.invoke(
                cli, ["assess", str(repo_path), "--config", str(config_path)]
            )

            # Should fail or fall back to defaults
            assert result.exit_code in [0, 1]

    def test_assess_nonexistent_config_file(self):
        """Test assess handles nonexistent config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            result = self.runner.invoke(
                cli,
                ["assess", str(repo_path), "--config", "/nonexistent/config.yml"],
            )

            # Should fail gracefully
            assert result.exit_code != 0

    def test_assess_large_output_directory_path(self):
        """Test assess handles very long output directory paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            # Create deeply nested output directory
            deep_path = Path(tmpdir) / "a" / "b" / "c" / "d" / "e" / "reports"

            result = self.runner.invoke(
                cli, ["assess", str(repo_path), "--output-dir", str(deep_path)]
            )

            # Should create nested directories and succeed
            assert result.exit_code == 0
            assert deep_path.exists()
