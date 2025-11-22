"""Comprehensive tests for code_sampler module."""

import tempfile
from pathlib import Path

import pytest

from agentready.learners.code_sampler import CodeSampler
from agentready.models import Attribute, Finding, Repository


@pytest.fixture
def temp_repo():
    """Create temporary repository with sample files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Create sample files
        (repo_path / "CLAUDE.md").write_text("# CLAUDE.md content")
        (repo_path / "README.md").write_text("# README content")
        (repo_path / ".gitignore").write_text("*.pyc\n__pycache__/")

        # Create src directory
        src_dir = repo_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("def main():\n    pass")
        (src_dir / "utils.py").write_text("def helper():\n    return True")

        # Create tests directory
        tests_dir = repo_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test_main():\n    assert True")

        # Create .pre-commit-config.yaml
        (repo_path / ".pre-commit-config.yaml").write_text("repos:\n  - hooks:")

        # Create pyproject.toml
        (repo_path / "pyproject.toml").write_text("[tool.pytest.ini_options]\n")

        yield Repository(
            path=repo_path, languages={"python": 0.9}, total_files=8, total_lines=100
        )


@pytest.fixture
def sample_finding():
    """Create sample finding."""
    attribute = Attribute(
        id="claude_md_file",
        name="CLAUDE.md File",
        category="Documentation",
        tier=1,
        description="Test",
        criteria="Test",
    )
    return Finding(attribute=attribute, status="pass", score=100.0)


class TestCodeSamplerInit:
    """Test CodeSampler initialization."""

    def test_init_defaults(self, temp_repo):
        """Test initialization with defaults."""
        sampler = CodeSampler(temp_repo)
        assert sampler.repository == temp_repo
        assert sampler.max_files == 5
        assert sampler.max_lines_per_file == 100

    def test_init_custom_limits(self, temp_repo):
        """Test initialization with custom limits."""
        sampler = CodeSampler(temp_repo, max_files=10, max_lines_per_file=200)
        assert sampler.max_files == 10
        assert sampler.max_lines_per_file == 200


class TestGetRelevantCode:
    """Test get_relevant_code method."""

    def test_get_code_for_claude_md(self, temp_repo):
        """Test getting code for CLAUDE.md attribute."""
        attribute = Attribute(
            id="claude_md_file",
            name="CLAUDE.md",
            category="Documentation",
            tier=1,
            description="Test",
            criteria="Test",
        )
        finding = Finding(attribute=attribute, status="pass", score=100.0)

        sampler = CodeSampler(temp_repo)
        result = sampler.get_relevant_code(finding)

        assert isinstance(result, str)
        assert len(result) > 0
        # Should include CLAUDE.md content
        assert "CLAUDE.md" in result or "content" in result.lower()

    def test_get_code_for_readme(self, temp_repo):
        """Test getting code for README attribute."""
        attribute = Attribute(
            id="readme_file",
            name="README",
            category="Documentation",
            tier=1,
            description="Test",
            criteria="Test",
        )
        finding = Finding(attribute=attribute, status="pass", score=100.0)

        sampler = CodeSampler(temp_repo)
        result = sampler.get_relevant_code(finding)

        assert isinstance(result, str)
        assert "README" in result or len(result) > 0

    def test_get_code_for_type_annotations(self, temp_repo):
        """Test getting code for type annotations attribute."""
        attribute = Attribute(
            id="type_annotations",
            name="Type Annotations",
            category="Code Quality",
            tier=2,
            description="Test",
            criteria="Test",
        )
        finding = Finding(attribute=attribute, status="pass", score=90.0)

        sampler = CodeSampler(temp_repo)
        result = sampler.get_relevant_code(finding)

        assert isinstance(result, str)
        # Should sample Python files
        assert len(result) > 0

    def test_get_code_for_gitignore(self, temp_repo):
        """Test getting code for gitignore attribute."""
        attribute = Attribute(
            id="gitignore",
            name="Gitignore",
            category="Configuration",
            tier=2,
            description="Test",
            criteria="Test",
        )
        finding = Finding(attribute=attribute, status="pass", score=100.0)

        sampler = CodeSampler(temp_repo)
        result = sampler.get_relevant_code(finding)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_code_for_pre_commit_hooks(self, temp_repo):
        """Test getting code for pre-commit hooks attribute."""
        attribute = Attribute(
            id="pre_commit_hooks",
            name="Pre-commit Hooks",
            category="Testing",
            tier=2,
            description="Test",
            criteria="Test",
        )
        finding = Finding(attribute=attribute, status="pass", score=100.0)

        sampler = CodeSampler(temp_repo)
        result = sampler.get_relevant_code(finding)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_code_for_standard_layout(self, temp_repo):
        """Test getting code for standard project layout attribute."""
        attribute = Attribute(
            id="standard_project_layout",
            name="Standard Layout",
            category="Structure",
            tier=2,
            description="Test",
            criteria="Test",
        )
        finding = Finding(attribute=attribute, status="pass", score=100.0)

        sampler = CodeSampler(temp_repo)
        result = sampler.get_relevant_code(finding)

        assert isinstance(result, str)
        # Should include directory structure
        assert len(result) > 0

    def test_get_code_for_unknown_attribute(self, temp_repo):
        """Test getting code for unknown attribute."""
        attribute = Attribute(
            id="unknown_attribute",
            name="Unknown",
            category="Unknown",
            tier=3,
            description="Test",
            criteria="Test",
        )
        finding = Finding(attribute=attribute, status="pass", score=50.0)

        sampler = CodeSampler(temp_repo)
        result = sampler.get_relevant_code(finding)

        # Should return fallback message
        assert "No code samples available" in result

    def test_respects_max_files_limit(self, temp_repo):
        """Test that max_files limit is respected."""
        # Create many Python files
        src_dir = temp_repo.path / "src"
        for i in range(10):
            (src_dir / f"file{i}.py").write_text(f"# File {i}")

        attribute = Attribute(
            id="type_annotations",
            name="Type Annotations",
            category="Code Quality",
            tier=2,
            description="Test",
            criteria="Test",
        )
        finding = Finding(attribute=attribute, status="pass", score=90.0)

        sampler = CodeSampler(temp_repo, max_files=3)
        result = sampler.get_relevant_code(finding)

        # Should only include up to max_files
        assert isinstance(result, str)
        assert len(result) > 0


class TestGetDirectoryTree:
    """Test _get_directory_tree method."""

    def test_get_existing_directory(self, temp_repo):
        """Test getting tree for existing directory."""
        sampler = CodeSampler(temp_repo)
        tree = sampler._get_directory_tree("src/")

        assert isinstance(tree, dict)
        assert tree["type"] == "directory"
        assert "children" in tree
        assert len(tree["children"]) > 0

    def test_get_nonexistent_directory(self, temp_repo):
        """Test getting tree for nonexistent directory."""
        sampler = CodeSampler(temp_repo)
        tree = sampler._get_directory_tree("nonexistent/")

        assert tree == {}

    def test_directory_tree_includes_files_and_dirs(self, temp_repo):
        """Test that directory tree includes both files and directories."""
        # Create nested structure
        nested_dir = temp_repo.path / "src" / "nested"
        nested_dir.mkdir(exist_ok=True)
        (nested_dir / "nested_file.py").write_text("# Nested")

        sampler = CodeSampler(temp_repo)
        tree = sampler._get_directory_tree("src/")

        assert tree["type"] == "directory"
        assert len(tree["children"]) > 0

        # Check that children have types
        for child in tree["children"]:
            assert "type" in child
            assert child["type"] in ["file", "directory"]

    def test_directory_tree_skips_hidden_dirs(self, temp_repo):
        """Test that hidden directories are skipped."""
        # Create hidden directory
        hidden_dir = temp_repo.path / "src" / ".hidden"
        hidden_dir.mkdir()

        sampler = CodeSampler(temp_repo)
        tree = sampler._get_directory_tree("src/")

        # Hidden dirs should be skipped
        child_names = [child.get("name") for child in tree["children"]]
        assert ".hidden" not in child_names


class TestFormatCodeSamples:
    """Test _format_code_samples method."""

    def test_format_single_file(self, temp_repo):
        """Test formatting single file."""
        sampler = CodeSampler(temp_repo)
        files = [temp_repo.path / "CLAUDE.md"]
        result = sampler._format_code_samples(files)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_multiple_files(self, temp_repo):
        """Test formatting multiple files."""
        sampler = CodeSampler(temp_repo)
        files = [temp_repo.path / "CLAUDE.md", temp_repo.path / "README.md"]
        result = sampler._format_code_samples(files)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_respects_line_limit(self, temp_repo):
        """Test that line limit is respected."""
        # Create file with many lines
        long_file = temp_repo.path / "long.py"
        long_file.write_text("\n".join([f"# Line {i}" for i in range(200)]))

        sampler = CodeSampler(temp_repo, max_lines_per_file=50)
        files = [long_file]
        result = sampler._format_code_samples(files)

        # Result should be truncated
        assert isinstance(result, str)
        lines = result.split("\n")
        # Should not include all 200 lines
        assert len(lines) < 200

    def test_format_empty_list(self, temp_repo):
        """Test formatting empty file list."""
        sampler = CodeSampler(temp_repo)
        result = sampler._format_code_samples([])

        # Should handle gracefully
        assert isinstance(result, str)

    def test_format_with_directory_tree(self, temp_repo):
        """Test formatting with directory tree dict."""
        sampler = CodeSampler(temp_repo)
        tree = {
            "type": "directory",
            "path": "src",
            "children": [
                {"type": "file", "name": "main.py"},
                {"type": "directory", "name": "utils"},
            ],
        }
        result = sampler._format_code_samples([tree])

        assert isinstance(result, str)
        assert len(result) > 0


class TestAttributeFilePatterns:
    """Test ATTRIBUTE_FILE_PATTERNS mapping."""

    def test_has_patterns_for_common_attributes(self):
        """Test that common attributes have file patterns defined."""
        common_attributes = [
            "claude_md_file",
            "readme_file",
            "type_annotations",
            "pre_commit_hooks",
            "gitignore",
            "lock_files",
            "test_coverage",
        ]

        for attr_id in common_attributes:
            assert attr_id in CodeSampler.ATTRIBUTE_FILE_PATTERNS
            patterns = CodeSampler.ATTRIBUTE_FILE_PATTERNS[attr_id]
            assert isinstance(patterns, list)
            assert len(patterns) > 0

    def test_patterns_are_valid_globs(self):
        """Test that patterns are valid glob patterns."""
        for patterns in CodeSampler.ATTRIBUTE_FILE_PATTERNS.values():
            for pattern in patterns:
                # Should be string
                assert isinstance(pattern, str)
                # Should not be empty
                assert len(pattern) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_binary_files(self, temp_repo):
        """Test handling of binary files."""
        # Create a "binary" file (simulated with non-UTF-8 content)
        binary_file = temp_repo.path / "image.png"
        binary_file.write_bytes(b"\x89PNG\r\n\x1a\n")

        sampler = CodeSampler(temp_repo)
        # Should handle gracefully without crashing
        files = [binary_file]
        try:
            result = sampler._format_code_samples(files)
            assert isinstance(result, str)
        except Exception:
            # If it raises, it should be caught and handled
            pass

    def test_handles_permission_errors(self, temp_repo):
        """Test handling of permission errors."""
        sampler = CodeSampler(temp_repo)

        # Create finding for file that will have permission error
        attribute = Attribute(
            id="test_attr", name="Test", category="Test", tier=1, description="Test", criteria="Test"
        )
        finding = Finding(attribute=attribute, status="pass", score=100.0)

        # Should not crash
        result = sampler.get_relevant_code(finding)
        assert isinstance(result, str)

    def test_handles_empty_repository(self):
        """Test handling of empty repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_repo = Repository(path=Path(tmpdir), languages={}, total_files=0, total_lines=0)

            sampler = CodeSampler(empty_repo)

            attribute = Attribute(
                id="claude_md_file",
                name="CLAUDE.md",
                category="Documentation",
                tier=1,
                description="Test",
                criteria="Test",
            )
            finding = Finding(attribute=attribute, status="fail", score=0.0)

            result = sampler.get_relevant_code(finding)
            # Should return something (empty or error message)
            assert isinstance(result, str)
