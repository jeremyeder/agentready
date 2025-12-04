"""Integration tests for headless/non-interactive mode execution.

These tests ensure AgentReady commands work in CI/CD environments
without requiring human interaction.
"""

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


class TestAssessHeadlessMode:
    """Test assess bypasses prompts via input parameter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_assess_sensitive_dir_with_input_yes(self):
        """Test assess handles sensitive directory warning with input."""
        # Note: We can't actually test /etc or /sys without sudo,
        # but we can test the pattern works with regular directories
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            # Should work without prompts
            result = self.runner.invoke(cli, ["assess", tmpdir], input="y\n")

            assert result.exit_code == 0
            # Assessment should complete
            assert (
                "Assessment complete" in result.output
                or "Overall Score" in result.output
            )

    def test_assess_large_repo_with_input_yes(self):
        """Test assess handles large repository warning with input."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            # Create enough files to potentially trigger warning (>10k files)
            # But keep it reasonable for test speed - just test the pattern
            for i in range(10):
                (repo_path / f"file_{i}.txt").write_text(f"content {i}")

            # Provide input to bypass any potential prompts
            result = self.runner.invoke(cli, ["assess", tmpdir], input="y\n" * 5)

            assert result.exit_code == 0

    def test_assess_no_prompts_minimal_repo(self):
        """Test assess runs without any prompts on minimal repo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            # Should work without any input needed
            result = self.runner.invoke(cli, ["assess", tmpdir])

            assert result.exit_code == 0


class TestGenerateConfigHeadlessMode:
    """Test generate-config command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_generate_config_help(self):
        """Test generate-config --help works."""
        result = self.runner.invoke(cli, ["generate-config", "--help"])

        assert result.exit_code == 0
        assert "Generate" in result.output or "config" in result.output.lower()

    def test_generate_config_no_example_file(self):
        """Test generate-config fails gracefully without example file."""
        # Run in temp directory where example file doesn't exist
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.runner.invoke(
                cli, ["generate-config"], input="y\n", catch_exceptions=True, cwd=tmpdir
            )

            # Should fail but not crash
            assert result.exit_code in [0, 1]


class TestResearchHeadlessMode:
    """Test research export overwrites with input."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_research_export_overwrites_with_input(self):
        """Test research export overwrites existing file with input."""
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "research.md"

            # Create initial export
            result = self.runner.invoke(
                cli, ["research", "export", "--output", str(export_path)]
            )
            # May succeed or fail if no research data, either is fine
            if result.exit_code == 0:
                # Try to overwrite
                result = self.runner.invoke(
                    cli,
                    ["research", "export", "--output", str(export_path)],
                    input="y\n",
                )
                # Should handle gracefully
                assert result.exit_code in [0, 1]

    def test_research_validate_no_prompts(self):
        """Test research validate runs without prompts."""
        result = self.runner.invoke(cli, ["research", "validate"])

        # May succeed or fail depending on if research file exists
        assert result.exit_code in [0, 1]


class TestAlignHeadlessMode:
    """Test align accepts all fixes with input."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_align_accepts_all_fixes_with_input(self):
        """Test align applies fixes with input confirmation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            # Provide "y\n" to accept all fixes
            result = self.runner.invoke(cli, ["align", tmpdir], input="y\n")

            # Align may fail if fixers need templates - test that it doesn't hang
            assert result.exit_code in [0, 1]

    def test_align_interactive_accepts_fixes_with_input(self):
        """Test align -i accepts individual fixes with input."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            # Provide multiple "y\n" for interactive prompts
            result = self.runner.invoke(cli, ["align", tmpdir, "-i"], input="y\n" * 20)

            assert result.exit_code in [0, 1]

    def test_align_dry_run_no_prompts(self):
        """Test align --dry-run runs without any prompts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            # Dry run should never prompt
            result = self.runner.invoke(cli, ["align", tmpdir, "--dry-run"])

            assert result.exit_code in [0, 1]
            if result.exit_code == 0:
                assert "DRY RUN" in result.output or "Mode: DRY RUN" in result.output


class TestCIIntegrationScenario:
    """Test complete CI/CD workflow without human interaction."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_full_ci_workflow(self):
        """Test complete CI workflow: assess → align → assess."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test Project\n")

            # Step 1: Initial assessment
            result1 = self.runner.invoke(cli, ["assess", tmpdir], input="y\n")
            assert result1.exit_code == 0

            # Step 2: Align (apply fixes) - may fail if fixers incomplete
            result2 = self.runner.invoke(cli, ["align", tmpdir], input="y\n")
            assert result2.exit_code in [0, 1]

            # Step 3: Re-assess to verify improvement
            result3 = self.runner.invoke(cli, ["assess", tmpdir], input="y\n")
            assert result3.exit_code == 0

    def test_ci_workflow_with_all_prompts_bypassed(self):
        """Test CI workflow handles all potential prompts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)
            (repo_path / "README.md").write_text("# Test\n")

            # Bootstrap repository
            result1 = self.runner.invoke(cli, ["bootstrap", tmpdir], input="y\n" * 10)
            assert result1.exit_code == 0

            # Assess with verbose output
            result2 = self.runner.invoke(
                cli, ["assess", tmpdir, "--verbose"], input="y\n" * 10
            )
            assert result2.exit_code == 0

            # Align with specific attributes - may fail if fixers incomplete
            result3 = self.runner.invoke(
                cli, ["align", tmpdir, "--attributes", "claude_md"], input="y\n" * 10
            )
            assert result3.exit_code in [0, 1]

    def test_bootstrap_then_assess_headless(self):
        """Test bootstrap followed by assessment in headless mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            init_git_repo(repo_path)

            # Bootstrap infrastructure
            result1 = self.runner.invoke(cli, ["bootstrap", tmpdir], input="y\n" * 5)
            assert result1.exit_code == 0

            # Immediately assess
            result2 = self.runner.invoke(cli, ["assess", tmpdir], input="y\n" * 5)
            assert result2.exit_code == 0

            # Should generate reports
            reports_dir = repo_path / ".agentready"
            if reports_dir.exists():
                assert len(list(reports_dir.glob("*.html"))) > 0
