# Coldstart Implementation Prompt: Align Subcommand (Automated Remediation)

**Priority**: P1
**Repository**: agentready (https://github.com/redhat/agentready)
**Branch Strategy**: Create feature branch from main

---

## Context

You are implementing a feature for AgentReady, a repository quality assessment tool for AI-assisted development.

### Repository Structure
```
agentready/
├── src/agentready/          # Source code
│   ├── models/              # Data models
│   ├── services/            # Scanner orchestration
│   ├── assessors/           # Attribute assessments
│   ├── reporters/           # Report generation (HTML, Markdown, JSON)
│   ├── templates/           # Jinja2 templates
│   └── cli/                 # Click-based CLI
├── tests/                   # Test suite (unit + integration)
├── examples/                # Example reports
└── specs/                   # Feature specifications
```

### Key Technologies
- Python 3.11+
- Click (CLI framework)
- Jinja2 (templating)
- Pytest (testing)
- Black, isort, ruff (code quality)

### Development Workflow
1. Create feature branch: `git checkout -b NNN-feature-name`
2. Implement changes with tests
3. Run linters: `black . && isort . && ruff check .`
4. Run tests: `pytest`
5. Commit with conventional commits
6. Create PR to main

---

## Feature Requirements

Align Subcommand (Automated Remediation)

**Priority**: P1 (Critical)

**Description**: Implement `agentready align` subcommand that automatically fixes failing attributes by generating and applying changes to the repository.

**Vision**: One command to align your repository with best practices - automatically create missing files, configure tooling, and improve code quality.

**Core Command**:

```bash
# Align repository to best practices
agentready align .

# Preview changes without applying
agentready align . --dry-run

# Apply specific attributes only
agentready align . --attributes claude_md_file,precommit_hooks

# Create GitHub PR instead of direct changes
agentready align . --create-pr

# Interactive mode (confirm each change)
agentready align . --interactive
```

**Supported Fixes**:

1. **Template-Based Fixes** (Auto-applicable):
   - `claude_md_file`: Generate CLAUDE.md from repository analysis
   - `gitignore_completeness`: Add missing patterns to .gitignore
   - `precommit_hooks`: Create .pre-commit-config.yaml with language-specific hooks
   - `readme_structure`: Scaffold missing README sections
   - `lock_files`: Generate lock files (package-lock.json, requirements.txt, etc.)
   - `issue_pr_templates`: Create .github/ISSUE_TEMPLATE and PULL_REQUEST_TEMPLATE
   - `conventional_commits`: Add commitlint configuration

2. **Command-Based Fixes** (Execute commands):
   - `lock_files`: Run `npm install`, `poetry lock`, `go mod tidy`
   - `precommit_hooks`: Run `pre-commit install`
   - `dependency_freshness`: Run `npm update`, `pip install --upgrade`

3. **AI-Powered Fixes** (Require LLM, optional):
   - `type_annotations`: Add type hints to Python functions
   - `inline_documentation`: Generate docstrings from function signatures
   - `cyclomatic_complexity`: Refactor high-complexity functions
   - `file_size_limits`: Split large files into smaller modules

**Workflow**:

```bash
# User runs alignment
$ agentready align . --dry-run

AgentReady Alignment Preview
============================

Repository: /Users/jeder/my-project
Current Score: 62.4/100 (Silver)
Projected Score: 84.7/100 (Gold) 🎯

Changes to be applied:

  ✅ claude_md_file (10 points)
     CREATE CLAUDE.md (1.2 KB)

  ✅ precommit_hooks (3 points)
     CREATE .pre-commit-config.yaml (845 bytes)
     RUN pre-commit install

  ✅ gitignore_completeness (3 points)
     MODIFY .gitignore (+15 patterns)

  ⚠️  type_annotations (10 points) - requires AI
     MODIFY 23 Python files (add type hints)
     Use --ai to enable AI-powered fixes

Total: 3 automatic fixes, 1 AI fix available
Apply changes? [y/N]
```

**Implementation**:

```python
# src/agentready/fixers/base.py
class BaseFixer(ABC):
    """Base class for attribute fixers."""

    @abstractmethod
    def can_fix(self, finding: Finding) -> bool:
        """Check if this fixer can fix the finding."""
        pass

    @abstractmethod
    def generate_fix(self, repository: Repository, finding: Finding) -> Fix:
        """Generate fix for the finding."""
        pass

# src/agentready/fixers/template_fixer.py
class TemplateFixer(BaseFixer):
    """Fixer that generates files from templates."""

    def generate_fix(self, repository: Repository, finding: Finding) -> Fix:
        template = self.load_template(finding.attribute.id)
        content = self.render_template(template, repository)
        return FileCreationFix(path="CLAUDE.md", content=content)

# src/agentready/cli/align.py
@cli.command()
@click.argument("repository", type=click.Path(exists=True), default=".")
@click.option("--dry-run", is_flag=True, help="Preview changes without applying")
@click.option("--create-pr", is_flag=True, help="Create GitHub PR instead of direct changes")
@click.option("--interactive", is_flag=True, help="Confirm each change")
@click.option("--attributes", help="Comma-separated attribute IDs to fix")
@click.option("--ai", is_flag=True, help="Enable AI-powered fixes (requires API key)")
def align(repository, dry_run, create_pr, interactive, attributes, ai):
    """Align repository with best practices by applying automatic fixes."""

    # Run assessment first
    assessment = run_assessment(repository)

    # Identify fixable failures
    failures = [f for f in assessment.findings if f.status == "fail"]
    fixable = identify_fixable_failures(failures, enable_ai=ai)

    # Generate fixes
    fixes = [fixer.generate_fix(repo, finding) for finding in fixable]

    # Preview changes
    show_fix_preview(fixes, assessment.overall_score, projected_score)

    if dry_run:
        return

    if interactive and not confirm_each_fix(fixes):
        return

    # Apply fixes
    if create_pr:
        create_github_pr_with_fixes(fixes)
    else:
        apply_fixes(fixes)

    # Re-run assessment to show improvement
    new_assessment = run_assessment(repository)
    show_improvement(assessment.overall_score, new_assessment.overall_score)
```

**Fix Types**:

```python
class Fix(ABC):
    """Base class for fixes."""
    attribute_id: str
    description: str

class FileCreationFix(Fix):
    """Create a new file."""
    path: Path
    content: str

class FileModificationFix(Fix):
    """Modify existing file."""
    path: Path
    changes: List[TextChange]

class CommandFix(Fix):
    """Execute command."""
    command: str
    working_dir: Path

class MultiStepFix(Fix):
    """Combination of multiple fixes."""
    steps: List[Fix]
```

**GitHub PR Integration**:

```bash
# Create PR with fixes
$ agentready align . --create-pr

Creating fix branch: agentready-align-20251121
Applying 3 fixes...
  ✅ Created CLAUDE.md
  ✅ Created .pre-commit-config.yaml
  ✅ Modified .gitignore

Committing changes...
Pushing to origin...

Created PR: https://github.com/redhat/my-project/pull/42
  Title: "Improve AgentReady score from 62.4 to 84.7 (Silver → Gold)"
  Score improvement: +22.3 points
  Attributes fixed: 3
```

**Configuration**:

```yaml
# .agentready-config.yaml
align:
  enabled: true

  auto_fix:
    # Attributes to automatically fix without confirmation
    - claude_md_file
    - gitignore_completeness
    - precommit_hooks

  confirm_before_fix:
    # Attributes requiring confirmation
    - type_annotations
    - cyclomatic_complexity

  never_fix:
    # Attributes to skip (user will fix manually)
    - container_setup
    - openapi_specs

  ai_fixes:
    enabled: false  # Require --ai flag
    provider: "anthropic"  # or "openai"
    model: "claude-3-5-sonnet-20241022"
    max_tokens: 4096
```

**Use Cases**:

**Use Case 1: New Repository Setup**
```bash
# Clone new project
git clone github.com/redhat/new-project
cd new-project

# Align to best practices
agentready align . --interactive

# Review and commit changes
git add .
git commit -m "chore: Align repository with AgentReady best practices"
```

**Use Case 2: Continuous Improvement**
```bash
# Weekly CI job to check and create alignment PRs
agentready align . --create-pr --dry-run
# If score < threshold, create PR automatically
```

**Use Case 3: Pre-commit Hook**
```bash
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: agentready-align
      name: AgentReady Alignment Check
      entry: agentready align --dry-run
      language: system
      pass_filenames: false
```

**Safety Features**:

- **Dry-run by default** for destructive operations
- **Git worktree** for isolated changes (optional)
- **Backup creation** before modifying files
- **Rollback support** if fixes fail
- **Validation** of generated files before writing
- **Interactive confirmation** for AI-powered fixes

**Related**: Automated remediation, repository improvement, onboarding

**Notes**:
- Start with template-based fixes (highest ROI, lowest risk)
- AI-powered fixes require API key and user consent
- Some attributes cannot be automatically fixed (requires human judgment)
- Consider integration with `git stash` for safety
- Could generate shell script of changes for manual review
- Align with Red Hat's AI-assisted development workflow

---


---

## Implementation Checklist

Before you begin:
- [ ] Read CLAUDE.md for project context
- [ ] Review existing similar features (if applicable)
- [ ] Understand the data model (src/agentready/models/)
- [ ] Check acceptance criteria in feature description

Implementation steps:
- [ ] Create feature branch
- [ ] Implement core functionality
- [ ] Add unit tests (target >80% coverage)
- [ ] Add integration tests (if applicable)
- [ ] Run linters and fix any issues
- [ ] Update documentation (README.md, CLAUDE.md if needed)
- [ ] Self-test the feature end-to-end
- [ ] Create PR with descriptive title and body

Code quality requirements:
- [ ] All code formatted with black (88 char lines)
- [ ] Imports sorted with isort
- [ ] No ruff violations
- [ ] All tests passing
- [ ] Type hints where appropriate
- [ ] Docstrings for public APIs

---

## Key Files to Review

Based on this feature, you should review:
- `src/agentready/models/` - Understand Assessment, Finding, Attribute models
- `src/agentready/services/scanner.py` - Scanner orchestration
- `src/agentready/assessors/base.py` - BaseAssessor pattern
- `src/agentready/reporters/` - Report generation
- `CLAUDE.md` - Project overview and guidelines
- `BACKLOG.md` - Full context of this feature

---

## Testing Strategy

For this feature, ensure:
1. **Unit tests** for core logic (80%+ coverage)
2. **Integration tests** for end-to-end workflows
3. **Edge case tests** (empty inputs, missing files, errors)
4. **Error handling tests** (graceful degradation)

Run tests:
```bash
# All tests
pytest

# With coverage
pytest --cov=src/agentready --cov-report=html

# Specific test file
pytest tests/unit/test_feature.py -v
```

---

## Success Criteria

This feature is complete when:
- ✅ All acceptance criteria from feature description are met
- ✅ Tests passing with >80% coverage for new code
- ✅ All linters passing (black, isort, ruff)
- ✅ Documentation updated
- ✅ PR created with clear description
- ✅ Self-tested end-to-end

---

## Questions to Clarify (if needed)

If anything is unclear during implementation:
1. Check CLAUDE.md for project patterns
2. Review similar existing features
3. Ask for clarification in PR comments
4. Reference the original backlog item

---

## Getting Started

```bash
# Clone and setup
git clone https://github.com/redhat/agentready.git
cd agentready

# Create virtual environment
uv venv && source .venv/bin/activate

# Install dependencies
uv pip install -e .
uv pip install pytest black isort ruff

# Create feature branch
git checkout -b 014-align-subcommand-(automated-remediation)

# Start implementing!
```

---

**Note**: This is a coldstart prompt. You have all context needed to implement this feature independently. Read the linked files, follow the patterns, and deliver high-quality code with tests.
