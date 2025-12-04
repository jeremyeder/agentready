---
layout: page
title: Developer Guide
---

Comprehensive guide for contributors and developers extending AgentReady.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Architecture Overview](#architecture-overview)
- [Implementing New Assessors](#implementing-new-assessors)
- [Testing Guidelines](#testing-guidelines)
- [Code Quality Standards](#code-quality-standards)
- [Contributing Workflow](#contributing-workflow)
- [Release Process](#release-process)

---

## Getting Started

### Prerequisites

- **Python 3.12 or 3.13**
- **Git**
- **uv** or **pip** (uv recommended for faster dependency management)
- **Make** (optional, for convenience commands)

### Fork and Clone

```bash
# Fork on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/agentready.git
cd agentready

# Add upstream remote
git remote add upstream https://github.com/ambient-code/agentready.git
```

### Install Development Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with development dependencies
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"

# Verify installation
pytest --version
black --version
ruff --version
```

---

## Development Environment

### Project Structure

```
agentready/
├── src/agentready/          # Source code
│   ├── cli/                 # Click-based CLI
│   │   └── main.py          # Entry point (assess, research-version, generate-config)
│   ├── models/              # Data models
│   │   ├── repository.py    # Repository representation
│   │   ├── attribute.py     # Attribute definition
│   │   ├── finding.py       # Assessment finding
│   │   └── assessment.py    # Complete assessment result
│   ├── services/            # Core business logic
│   │   ├── scanner.py       # Assessment orchestration
│   │   ├── scorer.py        # Score calculation
│   │   └── language_detector.py  # Language detection via git
│   ├── assessors/           # Attribute assessors
│   │   ├── base.py          # BaseAssessor abstract class
│   │   ├── documentation.py # CLAUDE.md, README assessors
│   │   ├── code_quality.py  # Type annotations, complexity
│   │   ├── testing.py       # Test coverage, pre-commit hooks
│   │   ├── structure.py     # Standard layout, gitignore
│   │   ├── repomix.py       # Repomix configuration assessor
│   │   └── stub_assessors.py # 9 stub assessors (22 implemented)
│   ├── reporters/           # Report generators
│   │   ├── html.py          # Interactive HTML with Jinja2
│   │   ├── markdown.py      # GitHub-Flavored Markdown
│   │   └── json.py          # Machine-readable JSON
│   ├── templates/           # Jinja2 templates
│   │   └── report.html.j2   # HTML report template
│   └── data/                # Bundled data
│       └── attributes.yaml  # Attribute definitions
├── tests/                   # Test suite
│   ├── unit/               # Unit tests (fast, isolated)
│   │   ├── test_models.py
│   │   ├── test_assessors_documentation.py
│   │   ├── test_assessors_code_quality.py
│   │   └── ...
│   ├── integration/        # End-to-end tests
│   │   └── test_full_assessment.py
│   └── fixtures/           # Test data
│       └── sample_repos/   # Sample repositories for testing
├── docs/                    # GitHub Pages documentation
├── examples/               # Example reports
│   └── self-assessment/    # AgentReady's own assessment
├── pyproject.toml          # Python package configuration
├── CLAUDE.md              # Project context for AI agents
├── README.md              # User-facing documentation
└── BACKLOG.md             # Feature backlog
```

### Development Tools

AgentReady uses modern Python tooling:

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **pytest** | Testing framework | `pyproject.toml` |
| **black** | Code formatter | `pyproject.toml` |
| **isort** | Import sorter | `pyproject.toml` |
| **ruff** | Fast linter | `pyproject.toml` |
| **mypy** | Type checker | `pyproject.toml` (future) |

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/agentready --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py -v

# Run tests matching pattern
pytest -k "test_claude_md" -v

# Run with output (don't capture print statements)
pytest -s

# Fast fail (stop on first failure)
pytest -x
```

**Recent Test Infrastructure Improvements (v1.27.2)**:

1. **Shared Test Fixtures** (`tests/conftest.py`):
   - Reusable repository fixtures for consistent test data
   - Reduced test code duplication
   - Faster test development

2. **Model Validation Enhancements**:
   - Enhanced Assessment schema validation
   - Path sanitization for cross-platform compatibility
   - Proper handling of optional fields

3. **Comprehensive Coverage**:
   - CLI tests (Phase 4) complete
   - Service module tests (Phase 3) complete
   - All 35 pytest failures from v1.27.0 resolved

**Current test coverage**: Focused on core logic (models, scoring, critical assessors)

### Code Quality Checks

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
ruff check src/ tests/

# Run all quality checks (recommended before committing)
black src/ tests/ && isort src/ tests/ && ruff check src/ tests/
```

### Pre-commit Hooks (Recommended)

Install pre-commit hooks to automatically run quality checks:

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

---

## Architecture Overview

AgentReady follows a **library-first architecture** with clear separation of concerns.

### Data Flow

```
Repository → Scanner → Assessors → Findings → Assessment → Reporters → Reports
                ↓
         Language Detection
         (git ls-files)
```

### Core Components

#### 1. Models (`models/`)

Immutable data classes representing domain entities:

- **Repository**: Path, name, detected languages
- **Attribute**: ID, name, tier, weight, description
- **Finding**: Attribute, status (pass/fail/skip), score, evidence, remediation
- **Assessment**: Repository, overall score, certification level, findings list

**Design Principles**:

- Immutable (frozen dataclasses)
- Type-annotated
- No business logic (pure data)
- Factory methods for common patterns (`Finding.create_pass()`, etc.)

#### 2. Services (`services/`)

Orchestration and core algorithms:

- **Scanner**: Coordinates assessment flow, manages assessors
- **Scorer**: Calculates weighted scores, determines certification levels
- **LanguageDetector**: Detects repository languages via `git ls-files`

**Design Principles**:

- Stateless (pure functions or stateless classes)
- Single responsibility
- No external dependencies (file I/O, network)
- Testable with mocks

#### 3. Assessors (`assessors/`)

Strategy pattern implementations for each attribute:

- **BaseAssessor**: Abstract base class defining interface
- Concrete assessors: `CLAUDEmdAssessor`, `READMEAssessor`, etc.

**Design Principles**:

- Each assessor is independent
- Inherit from `BaseAssessor`
- Implement `assess(repository)` method
- Return `Finding` object
- Fail gracefully (return "skipped" if tools missing, don't crash)

#### 4. Reporters (`reporters/`)

Transform `Assessment` into report formats:

- **HTMLReporter**: Jinja2-based interactive report
- **MarkdownReporter**: GitHub-Flavored Markdown
- **JSONReporter**: Machine-readable JSON

**Design Principles**:

- Take `Assessment` as input
- Return formatted string
- Self-contained (HTML has inline CSS/JS, no CDN)
- Idempotent (same input → same output)

### Key Design Patterns

#### Strategy Pattern (Assessors)

Each assessor is a pluggable strategy implementing the same interface:

```python
from abc import ABC, abstractmethod

class BaseAssessor(ABC):
    @property
    @abstractmethod
    def attribute_id(self) -> str:
        """Unique attribute identifier."""
        pass

    @abstractmethod
    def assess(self, repository: Repository) -> Finding:
        """Assess repository for this attribute."""
        pass

    def is_applicable(self, repository: Repository) -> bool:
        """Check if this assessor applies to the repository."""
        return True
```

#### Factory Pattern (Finding Creation)

`Finding` class provides factory methods for common patterns:

```python
# Pass with full score
finding = Finding.create_pass(
    attribute=attribute,
    evidence="Found CLAUDE.md at repository root",
    remediation=None
)

# Fail with zero score
finding = Finding.create_fail(
    attribute=attribute,
    evidence="No CLAUDE.md file found",
    remediation=Remediation(steps=[...], tools=[...])
)

# Skip (not applicable)
finding = Finding.create_skip(
    attribute=attribute,
    reason="Not implemented yet"
)
```

#### Template Pattern (Reporters)

Reporters use Jinja2 templates for HTML generation:

```python
from jinja2 import Environment, FileSystemLoader

class HTMLReporter:
    def generate(self, assessment: Assessment) -> str:
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('report.html.j2')
        return template.render(assessment=assessment)
```

---

## Bootstrap System Architecture

Bootstrap automates infrastructure generation through template rendering and language detection. The flow is: Repository → LanguageDetector (identifies primary language via file extensions) → BootstrapGenerator (renders Jinja2 templates with context) → Generated Files (workflows, configs, templates).

**Core components**: `BootstrapGenerator` orchestrates template rendering with methods for language detection, template selection, rendering, and file writing (never overwrites existing files). CLI (`cli/bootstrap.py`) provides `--dry-run` for preview and `--language` for manual override. Templates are organized in `templates/bootstrap/` with language-specific subdirectories (python/, javascript/, go/) and common/ for shared templates (CODEOWNERS, issue templates, PR template).

**Template context variables**: All templates receive repository_name, detected language, directory existence flags (has_tests_directory, has_src_directory), language version (python_version, node_version, go_version), current year, and organization name from git remote.

**Language detection**: LanguageDetector maps file extensions (.py → Python, .js → JavaScript, .go → Go) and counts files by language to identify the primary language (most files). Manual override via `--language python|javascript|go|auto` flag.

**File generation flow**: Detect language (auto or manual) → Select language-specific templates → Render each template with context → Check if file exists (skip if yes) → Write file (or preview in dry-run mode) → Return list of GeneratedFile objects with paths and creation status.

**Error handling**: Custom exceptions (BootstrapError, LanguageDetectionError, TemplateRenderError, FileWriteError) handle scenarios like non-git repositories (fail early), language detection failure (require --language flag), missing templates (report name), existing files (skip gracefully), and permission issues (report path with suggested fix).

**Dry-run mode**: When `--dry-run` is true, templates are rendered but files aren't written. Returns GeneratedFile objects with `created=False` and `dry_run=True` flags to show what would be created without modifying the repository.

---

## Creating Bootstrap Templates

Bootstrap templates are Jinja2 files in `templates/bootstrap/` with language-specific subdirectories (python/, javascript/, go/) and common/ for shared templates. Templates use variables like `{% raw %}{{ python_version }}{% endraw %}`, `{% raw %}{{ repository_name }}{% endraw %}`, `{% raw %}{{ year }}{% endraw %}`, and conditionals for language-specific logic (`{% raw %}{% if language == "python" %}...{% endif %}{% endraw %}`).

**Development workflow**: Create template file (e.g., `python/mytemplate.yml.j2`), add Jinja2 variables and conditionals, register in BootstrapGenerator's TEMPLATES dict, test with `agentready bootstrap . --dry-run`, verify output.

**Best practices**: Use descriptive variable names (`{% raw %}{{ python_version }}{% endraw %}` not `{% raw %}{{ ver }}{% endraw %}`), provide defaults (`{% raw %}{{ python_version | default("3.11") }}{% endraw %}`), add generation metadata comments, handle optional sections with conditionals (`{% raw %}{% if has_tests_directory %}{% endraw %}`), include context about template purpose.

---

## Implementing New Assessors

Check `stub_assessors.py` for unimplemented attributes. Create assessor class inheriting from `BaseAssessor` with required methods: `attribute_id` property returning unique ID, `assess(repository)` method returning Finding object, optional `is_applicable(repository)` for language-specific logic. Use `calculate_proportional_score(actual, target)` for partial compliance (e.g., 60% coverage of 80% target = score of 75).

**Implementation pattern**: Check language applicability (skip if not applicable) → Count/analyze repository content → Calculate coverage/score → Return pass/fail/skip Finding with evidence and remediation. Provide rich remediation including specific steps, required tools, example commands, code examples, and citation sources (PEP 257, Google Style Guides, etc.).

Register in `services/scanner.py` assessor list. Write comprehensive tests in `tests/unit/test_assessors_*.py` covering pass/fail/skip scenarios using pytest fixtures and tmp_path. Run `pytest tests/unit/test_assessors_*.py -v` to verify.

**Best practices**: Fail gracefully (return "skipped" if tools missing), use stdlib when possible (ast, re, pathlib), keep assessments fast (<1s), provide actionable evidence with file paths and counts.

---

## Testing Guidelines

Tests organized in `tests/unit/` (fast, isolated, mocked) and `tests/integration/` (end-to-end workflows). Use descriptive naming (`test_what_when_expected`), Arrange-Act-Assert pattern, pytest fixtures for reusable test data. Target >80% coverage for new code, 100% for critical paths (scoring, finding creation). Run `pytest --cov=src/agentready --cov-report=html` to generate coverage reports

---

## Code Quality Standards

Run `black src/ tests/` for formatting (88 char line length, opinionated), `isort src/ tests/` for import sorting (black-compatible profile), `ruff check src/ tests/` for linting (selects E/F/W/I rules, ignores E501). All configured in `pyproject.toml`. Use Google-style docstrings for all public functions/classes/methods with full type hints on parameters and return types

---

## Contributing Workflow

Create feature branch from main (`git checkout -b feature/name`), implement changes following style guide with comprehensive tests and updated docs. Run quality checks (`black src/ tests/ && isort src/ tests/ && ruff check src/ tests/ && pytest --cov` - all must pass). Commit using conventional commits (feat/fix/docs/test/refactor/chore prefix). Push and create PR with clear title/description, include what/why/testing/checklist. Address review feedback on same branch.

---

## Release Process

Follows semantic versioning (Major.Minor.Patch for breaking/features/fixes). Update version in pyproject.toml and CHANGELOG.md, run full tests and quality checks, build package (`python -m build`), test locally, create and push git tag (`vX.Y.Z`), upload to PyPI (`twine upload dist/*`), create GitHub release with changelog

---

## Additional Resources

- **[API Reference](api-reference.html)** — Public API documentation
- **[Examples](examples.html)** — Real-world assessment reports
- **CLAUDE.md** — Project context for AI agents
- **BACKLOG.md** — Planned features and enhancements

---

**Ready to contribute?** Check out [good first issues](https://github.com/ambient-code/agentready/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) on GitHub!
