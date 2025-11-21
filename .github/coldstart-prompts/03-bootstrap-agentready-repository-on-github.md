# Coldstart Implementation Prompt: Bootstrap AgentReady Repository on GitHub

**Priority**: P0
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

Bootstrap AgentReady Repository on GitHub

**Priority**: P0 (Critical - Dogfooding)

**Description**: Implement `agentready bootstrap` command to set up the agentready repository itself on GitHub with all best practices. This is the FIRST feature to implement - we'll dogfood our own tool!

**Vision**: Use AgentReady to bootstrap the AgentReady repository - demonstrating the tool's value while setting up our own infrastructure.

**Why P0**:
- Demonstrates tool value immediately (dogfooding)
- Sets up critical GitHub infrastructure (Actions, badges, PR templates)
- Validates bootstrap command design before external users
- Creates the foundation for GitHub App integration

**Requirements**:

1. **GitHub Repository Setup**
   - Create/update repository on GitHub via `gh` CLI
   - Set repository description and topics
   - Configure repository settings (PR requirements, branch protection)

2. **GitHub Actions Workflows**
   - `.github/workflows/agentready-assessment.yml` - Run assessment on PR/push
   - `.github/workflows/tests.yml` - Run pytest, linters
   - `.github/workflows/release.yml` - Publish to PyPI (future)

3. **GitHub Templates**
   - `.github/ISSUE_TEMPLATE/bug_report.md`
   - `.github/ISSUE_TEMPLATE/feature_request.md`
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `.github/CODEOWNERS`

4. **Pre-commit Hooks**
   - `.pre-commit-config.yaml` with black, isort, ruff
   - Conventional commit linting (commitlint)
   - Auto-run tests before commit

5. **Dependency Management**
   - Dependabot configuration (`.github/dependabot.yml`)
   - Security scanning (`.github/workflows/security.yml`)

6. **Documentation Updates**
   - Update README.md with badges
   - Add CONTRIBUTING.md
   - Add CODE_OF_CONDUCT.md (Red Hat standard)
   - Add LICENSE (Apache 2.0 or MIT)

**Command Interface**:

```bash
# Bootstrap current repository on GitHub
agentready bootstrap .

# Bootstrap with specific language
agentready bootstrap . --language python

# Bootstrap and create GitHub repo
agentready bootstrap . --create-repo redhat/agentready

# Dry run (show what would be created)
agentready bootstrap . --dry-run

# Interactive mode (confirm each file)
agentready bootstrap . --interactive
```

**What Gets Created**:

```
.github/
├── workflows/
│   ├── agentready-assessment.yml  # Run assessment on PR
│   ├── tests.yml                  # Run tests and linters
│   └── dependabot.yml            # Dependency updates
├── ISSUE_TEMPLATE/
│   ├── bug_report.md
│   └── feature_request.md
├── PULL_REQUEST_TEMPLATE.md
├── CODEOWNERS
└── dependabot.yml

.pre-commit-config.yaml
CONTRIBUTING.md
CODE_OF_CONDUCT.md
LICENSE
```

**GitHub Actions Workflow Example**:

```yaml
# .github/workflows/agentready-assessment.yml
name: AgentReady Assessment

on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main]

jobs:
  assess:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install AgentReady
        run: |
          pip install agentready

      - name: Run Assessment
        run: |
          agentready assess . --verbose

      - name: Upload Reports
        uses: actions/upload-artifact@v4
        with:
          name: agentready-reports
          path: .agentready/

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('.agentready/report-latest.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

**Implementation Phases**:

**Phase 1: Core Bootstrap** (This Sprint)
- Implement `agentready bootstrap` command
- Create template files for GitHub Actions, pre-commit, templates
- Test on agentready repository itself
- Commit all generated files

**Phase 2: GitHub Integration** (Next Sprint)
- Use `gh` CLI to create/update repository
- Set up branch protection rules
- Configure repository settings
- Add repository badges

**Phase 3: Language-Specific Templates** (Future)
- Python-specific templates (pytest, black, mypy)
- JavaScript-specific (eslint, prettier, jest)
- Go-specific (golangci-lint, gotestsum)

**Files to Create**:

```
src/agentready/
├── cli/bootstrap.py           # Bootstrap CLI command
├── bootstrap/
│   ├── __init__.py
│   ├── generator.py          # File generator
│   ├── github_setup.py       # GitHub integration
│   └── templates/            # Template files
│       ├── github/
│       │   ├── workflows/
│       │   │   ├── agentready.yml.j2
│       │   │   └── tests.yml.j2
│       │   ├── ISSUE_TEMPLATE/
│       │   └── PULL_REQUEST_TEMPLATE.md.j2
│       ├── precommit.yaml.j2
│       ├── CONTRIBUTING.md.j2
│       └── CODE_OF_CONDUCT.md.j2
tests/unit/test_bootstrap.py
```

**Acceptance Criteria**:

- [ ] `agentready bootstrap .` creates all required files
- [ ] GitHub Actions workflows are valid and functional
- [ ] Pre-commit hooks install and run successfully
- [ ] Repository badges added to README.md
- [ ] Dry-run mode shows what would be created
- [ ] Interactive mode prompts for confirmation
- [ ] Successfully bootstrap agentready repository itself
- [ ] All generated files committed to agentready repo
- [ ] GitHub Actions runs assessment on every PR

**Success Metrics**:

- AgentReady repository on GitHub has:
  - ✅ GitHub Actions running assessments
  - ✅ PR template with checklist
  - ✅ Issue templates for bugs/features
  - ✅ Pre-commit hooks configured
  - ✅ Dependabot enabled
  - ✅ Repository badge showing score
  - ✅ All linters passing in CI

**Priority Justification**:

This is P0 because:
1. **Dogfooding** - We need this for our own repository first
2. **Demonstrates value** - Shows AgentReady in action on itself
3. **Foundation** - Required before GitHub App integration
4. **Credibility** - Can't tell others to use it if we don't use it ourselves

**Related**: GitHub App Integration (#5), Align Command (#3)

**Notes**:
- Start with Python-specific templates (our use case)
- Keep templates simple and focused
- Use Jinja2 for template rendering
- Integrate with `gh` CLI for GitHub operations
- All templates should pass AgentReady assessment!

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
git checkout -b 003-bootstrap-agentready-repository-on-github

# Start implementing!
```

---

**Note**: This is a coldstart prompt. You have all context needed to implement this feature independently. Read the linked files, follow the patterns, and deliver high-quality code with tests.
