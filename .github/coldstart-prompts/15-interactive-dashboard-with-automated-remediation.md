# Coldstart Implementation Prompt: Interactive Dashboard with Automated Remediation

**Priority**: P2
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

Interactive Dashboard with Automated Remediation

**Priority**: P2 (High Value)

**Description**: Transform the static HTML report into an interactive dashboard that enables one-click remediation via automated GitHub issue creation and draft PR generation.

**Vision**: "How to Align Your Repo with Best Practices" - Click a button → Open GitHub issue with draft PR containing fixes.

**Core Features**:

1. **Interactive Dashboard Mode**
   - Real-time assessment (WebSocket updates)
   - Live filtering and sorting (already have this)
   - Action buttons on each failing attribute
   - Progress tracking across multiple runs
   - Historical trend visualization

2. **One-Click Remediation Actions**
   - "Fix This" button on each failing attribute
   - Generates GitHub issue automatically
   - Creates draft PR with proposed changes
   - Links issue to PR
   - Assigns to repository owner/team

3. **Automated Fix Generation**
   - Template-based fixes for common issues:
     - Missing .gitignore → Generate language-specific .gitignore
     - No CLAUDE.md → Generate template with repo analysis
     - Missing pre-commit hooks → Add .pre-commit-config.yaml
     - No lock files → Generate appropriate lock file
     - Missing README sections → Scaffold missing sections
   - AI-powered fixes for complex issues:
     - Refactor high-complexity functions
     - Add type annotations to functions
     - Generate docstrings from function signatures
     - Split large files

4. **GitHub Integration**
   - OAuth authentication with GitHub
   - gh CLI integration for seamless workflow
   - Create issues via GitHub API
   - Create draft PRs via GitHub API
   - Auto-label issues (e.g., `agentready`, `automated-fix`, `tier-1-essential`)
   - Link to AgentReady assessment report

**Technical Architecture**:

```yaml
# New components needed:

Backend (Optional - could be fully client-side with gh CLI):
  - GitHub OAuth app for authentication
  - Issue/PR template generator
  - Fix generator service (template-based + AI-powered)
  - Assessment history tracker

Frontend (Enhanced HTML report):
  - Action buttons with loading states
  - GitHub auth flow UI
  - Progress indicators
  - Toast notifications for actions
  - Modal dialogs for fix preview

CLI Extensions:
  - agentready dashboard .  # Launch local web server
  - agentready fix <attribute-id>  # Generate fix for specific attribute
  - agentready create-issue <attribute-id>  # Create GitHub issue
  - agentready create-pr <attribute-id>  # Create draft PR
```

**Use Cases**:

**Use Case 1: Quick Fixes**
```bash
# User runs assessment
agentready assess . --dashboard

# Opens dashboard in browser at http://localhost:8000
# User clicks "Fix This" on "Missing CLAUDE.md"
# → Creates issue: "Add CLAUDE.md configuration file"
# → Creates draft PR with generated CLAUDE.md template
# → PR includes: project analysis, detected languages, suggested structure
```

**Use Case 2: Batch Remediation**
```bash
# Dashboard shows all failures
# User selects multiple attributes
# Clicks "Fix All Selected"
# → Creates single issue: "Improve AgentReady Score from Silver to Gold"
# → Creates draft PR with all fixes
# → PR description includes before/after score projection
```

**Use Case 3: CI/CD Integration**
```bash
# GitHub Action runs assessment
# Posts comment on PR with assessment results
# Includes links to create remediation issues
# Can auto-create draft PR for improvements
```

**Implementation Approach**:

**Phase 1: Client-Side with gh CLI** (Simplest, no backend needed)
- Use JavaScript in HTML report to call gh CLI via local proxy
- Generate fix files locally
- Use `gh issue create` and `gh pr create`
- Works for users with gh CLI installed

**Phase 2: Dashboard Server** (Enhanced UX)
- Flask/FastAPI server serving dashboard
- WebSocket for live updates
- GitHub OAuth for authentication
- Background workers for fix generation

**Phase 3: Cloud Service** (SaaS offering)
- Hosted dashboard at agentready.dev
- GitHub App installation
- Webhook integration for continuous monitoring
- Team collaboration features

**Fix Templates by Attribute**:

```yaml
claude_md_file:
  type: template
  generates:
    - file: CLAUDE.md
      content: |
        # {repository_name}

        ## Overview
        {auto_generated_description}

        ## Architecture
        {detected_patterns}

        ## Development
        {build_commands}

lock_files:
  type: command
  commands:
    - condition: has_package_json
      run: npm install
    - condition: has_pyproject_toml
      run: poetry lock || pip freeze > requirements.txt

precommit_hooks:
  type: template
  generates:
    - file: .pre-commit-config.yaml
      content: {language_specific_hooks}

readme_structure:
  type: enhancement
  modifies: README.md
  adds_sections:
    - Installation
    - Usage
    - Development
    - Contributing

type_annotations:
  type: ai_powered
  uses: ast_analysis + llm
  modifies: "*.py"
  adds: type_hints
```

**Dashboard vs Report Decision**:

**Keep Both**:
- Static reports for CI/CD, documentation, archiving
- Dashboard for interactive development workflow
- Reports can link to dashboard for remediation
- Dashboard can export static reports

**Benefits of Dashboard**:
- ✅ Interactive remediation workflow
- ✅ Live assessment updates
- ✅ Progress tracking over time
- ✅ Team collaboration (comments, assignments)
- ✅ Automated fix preview before applying
- ✅ Integration with existing tools (GitHub, IDEs)

**Challenges**:
- Authentication complexity (GitHub OAuth)
- Fix generation quality (need good templates + AI)
- PR review overhead (lots of automated PRs)
- Maintaining fix templates as best practices evolve

**Recommended Approach**:

1. **Start with enhanced static report**:
   - Add "Create Issue" buttons that generate gh CLI commands
   - Users copy/paste commands to create issues
   - Include fix templates in issue descriptions

2. **Add local dashboard** (Phase 2):
   - Flask server with WebSocket updates
   - GitHub integration via gh CLI
   - Generate fixes, preview diffs, create PRs

3. **Consider hosted service** (Phase 3+):
   - If adoption is high
   - SaaS model for teams
   - Continuous monitoring and recommendations

**Related**: GitHub integration, automation, remediation, UX

**Notes**:
- This is a MAJOR feature that could become a standalone product
- Consider MVP: "Copy this gh command" buttons in HTML report
- AI-powered fix generation requires careful validation
- Some fixes (like refactoring) need human review
- Could integrate with existing tools (Dependabot, Renovate)
- May want to partner with GitHub for official integration

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
git checkout -b 015-interactive-dashboard-with-automated-remediation

# Start implementing!
```

---

**Note**: This is a coldstart prompt. You have all context needed to implement this feature independently. Read the linked files, follow the patterns, and deliver high-quality code with tests.
