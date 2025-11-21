# Coldstart Implementation Prompt: Report Header with Repository Metadata

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

Report Header with Repository Metadata

**Priority**: P0 (Critical - Blocking Usability)

**Description**: Add prominent report header showing what repository/agent/code was scanned. Currently reports lack context about what was assessed.

**Problem**: Users cannot identify what the report is about without digging into the details. No repository name, path, timestamp, or assessment context visible at the top.

**Requirements**:
- **Prominent header section** at the top of all report formats (HTML, Markdown, JSON)
- Repository name (bold, large font)
- Repository path (absolute path on filesystem or GitHub URL)
- Assessment timestamp (human-readable: "November 21, 2025 at 2:11 AM")
- Branch name and commit hash
- AgentReady version used for assessment
- Who ran the assessment (username@hostname)
- Command used: `agentready assess /path/to/repo --verbose`

**HTML Report Header Design**:
```html
<header class="report-header">
  <div class="repo-info">
    <h1>AgentReady Assessment Report</h1>
    <div class="repo-name">Repository: agentready</div>
    <div class="repo-path">/Users/jeder/repos/sk/agentready</div>
    <div class="repo-git">Branch: 001-agentready-scorer | Commit: d49947c</div>
  </div>
  <div class="meta-info">
    <div>Assessed: November 21, 2025 at 2:11 AM</div>
    <div>AgentReady Version: 1.0.0</div>
    <div>Run by: jeder@macbook</div>
  </div>
</header>
```

**Markdown Report Header**:
```markdown
# 🤖 AgentReady Assessment Report

**Repository**: agentready
**Path**: `/Users/jeder/repos/sk/agentready`
**Branch**: `001-agentready-scorer` | **Commit**: `d49947c`
**Assessed**: November 21, 2025 at 2:11 AM
**AgentReady Version**: 1.0.0
**Run by**: jeder@macbook

---
```

**JSON Report Metadata**:
```json
{
  "metadata": {
    "agentready_version": "1.0.0",
    "assessment_timestamp": "2025-11-21T02:11:05Z",
    "assessment_timestamp_human": "November 21, 2025 at 2:11 AM",
    "executed_by": "jeder@macbook",
    "command": "agentready assess . --verbose",
    "working_directory": "/Users/jeder/repos/sk/agentready"
  },
  "repository": { ... }
}
```

**Implementation**:
- Add metadata collection to Scanner
- Update all reporter templates (HTML, Markdown)
- Enhance Assessment model with metadata field
- Position header prominently (before score summary)

**Acceptance Criteria**:
- ✅ User can immediately identify what repository was assessed
- ✅ Timestamp shows when assessment was run
- ✅ Git context (branch, commit) visible
- ✅ AgentReady version tracked for reproducibility

**Related**: Report generation, usability, debugging

**Notes**:
- This is blocking adoption - users confused about report context
- Critical for multi-repository workflows
- Needed for CI/CD integration (track which build)

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
git checkout -b 004-report-header-with-repository-metadata

# Start implementing!
```

---

**Note**: This is a coldstart prompt. You have all context needed to implement this feature independently. Read the linked files, follow the patterns, and deliver high-quality code with tests.
