# Coldstart Implementation Prompt: GitHub App Integration (Badge & Status Checks)

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

GitHub App Integration (Badge & Status Checks)

**Priority**: P2 (High Value)

**Description**: Create a GitHub App that provides badge integration, PR status checks, and automated assessment comments to help Red Hat engineering teams track and improve repository quality.

**Core Features**:

1. **Repository Badge**
   - Shields.io-compatible SVG badge showing certification level
   - Endpoint: `https://agentready.redhat.com/badge/{owner}/{repo}.svg`
   - Dynamic color based on certification (Platinum=purple, Gold=yellow, Silver=silver, Bronze=brown)
   - Include score: "AgentReady: 85.2 (Gold)"
   - Click badge to view latest assessment report

2. **GitHub Actions Integration**
   - Create official `agentready/assess-action` GitHub Action
   - Run assessment on PR events (opened, synchronized, reopened)
   - Run assessment on push to main/master
   - Support custom triggers via workflow_dispatch

3. **PR Status Checks**
   - Use GitHub Commit Status API to report assessment results
   - Set check status: success (>90), warning (75-89), failure (<75)
   - Configurable thresholds via `.agentready-config.yaml`
   - Block PR merge if score below threshold (optional)
   - Link to detailed HTML report in check details

4. **PR Comments**
   - Automated bot comments on PRs with assessment summary
   - Show score delta: "Score changed: 72.4 → 78.3 (+5.9)"
   - List new failures and fixes
   - Collapsible sections for full findings
   - Trend chart showing last 10 assessments (ASCII or embedded image)
   - Include remediation suggestions for new failures

**Technical Implementation**:

**Phase 1: GitHub Actions Integration**
```yaml
# .github/workflows/agentready.yml
name: AgentReady Assessment
on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main, master]

jobs:
  assess:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: agentready/assess-action@v1
        with:
          threshold: 75
          post-comment: true
          update-status: true
```

**Phase 2: Badge Service**
```python
# FastAPI endpoint for badge generation
@app.get("/badge/{owner}/{repo}.svg")
async def get_badge(owner: str, repo: str):
    # Fetch latest assessment from GitHub Actions artifacts
    # Or run quick assessment on-demand
    score, level = get_latest_assessment(owner, repo)
    color = LEVEL_COLORS[level]
    return SVGResponse(generate_badge(score, level, color))
```

**Phase 3: GitHub App**
- App permissions: Contents (read), Checks (write), Pull requests (write)
- Webhook events: push, pull_request
- Installed via GitHub Marketplace (Red Hat internal)
- Dashboard at agentready.redhat.com showing:
  - Repository list with scores
  - Historical trends
  - Organization-wide statistics
  - Top repositories by improvement

**Integration Points**:

1. **GitHub Actions Artifacts**
   - Store assessment reports as workflow artifacts
   - Keep last 30 days of reports for trend analysis
   - Generate downloadable HTML/JSON/Markdown reports

2. **GitHub Status API**
   ```python
   POST /repos/{owner}/{repo}/statuses/{commit_sha}
   {
     "state": "success",  # or "pending", "failure", "error"
     "target_url": "https://agentready.redhat.com/reports/{run_id}",
     "description": "AgentReady: 85.2 (Gold)",
     "context": "agentready/assessment"
   }
   ```

3. **GitHub Checks API** (preferred over Status API)
   ```python
   POST /repos/{owner}/{repo}/check-runs
   {
     "name": "AgentReady Assessment",
     "status": "completed",
     "conclusion": "success",
     "output": {
       "title": "Score: 85.2/100 (Gold)",
       "summary": "Passed 20/25 attributes",
       "text": "Detailed findings..."
     }
   }
   ```

**Use Cases**:

**Use Case 1: Add Badge to README**
```markdown
# My Project

[![AgentReady](https://agentready.redhat.com/badge/redhat/my-project.svg)](https://agentready.redhat.com/reports/redhat/my-project)
```

**Use Case 2: Enforce Quality Gates**
```yaml
# .agentready-config.yaml
github:
  status_checks:
    enabled: true
    min_score: 75  # Block merge if score < 75
    require_improvement: true  # Block if score decreased
```

**Use Case 3: Track Organization Progress**
- Dashboard shows all repos in Red Hat org
- Filter by team, language, certification level
- Identify repos needing attention
- Celebrate improvements (score increases)

**Configuration**:

```yaml
# .agentready-config.yaml
github:
  badge:
    enabled: true
    style: flat-square  # or flat, plastic, for-the-badge
    label: "AgentReady"

  actions:
    enabled: true
    trigger_on: [pull_request, push]
    post_comment: true
    update_status: true
    upload_artifacts: true

  status_checks:
    enabled: true
    min_score: 75
    require_improvement: false

  comments:
    enabled: true
    show_delta: true
    show_trend: true
    collapse_details: true
```

**Implementation Checklist**:

- [ ] Create `agentready/assess-action` GitHub Action
- [ ] Implement badge generation service
- [ ] Add GitHub Status API integration
- [ ] Add GitHub Checks API integration
- [ ] Implement PR comment generation
- [ ] Add score delta calculation
- [ ] Create assessment artifact storage
- [ ] Build organization dashboard
- [ ] Add Red Hat SSO authentication
- [ ] Deploy to Red Hat infrastructure
- [ ] Create documentation for Red Hat teams
- [ ] Add to Red Hat developer onboarding

**Related**: CI/CD integration, automation, visibility, quality gates

**Notes**:
- Focus on internal Red Hat adoption first
- Badge service could be hosted on Red Hat infrastructure
- Dashboard should integrate with Red Hat IdM for authentication
- Consider integration with Red Hat's existing code quality tools
- GitHub App should be installable via Red Hat GitHub Enterprise
- All data stays within Red Hat infrastructure (no external services)
- Align with Red Hat's OpenShift AI strategy for agentic development
- Could become part of Red Hat's AI-assisted development workflow

---

## Backlog Metadata

**Created**: 2025-11-21
**Last Updated**: 2025-11-21
**Total Items**: 14 (11 original + 3 from code review)

## Priority Summary

- **P0 (Critical)**: 4 items - Security/Logic Bugs (FIX FIRST!), Bootstrap Command, Report Header Metadata, HTML Design Improvements
- **P1 (Critical)**: 4 items - Code Quality Fixes, Test Coverage Improvements, Align Subcommand
- **P2 (High Value)**: 3 items - Security Polish, Interactive Dashboard, GitHub App Integration
- **P3 (Important)**: 2 items - Report Schema Versioning, AgentReady Repository Agent
- **P4 (Enhancement)**: 3 items - Research Report Utility, Repomix Integration, Customizable Themes


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
git checkout -b 016-github-app-integration-(badge-&-status-checks)

# Start implementing!
```

---

**Note**: This is a coldstart prompt. You have all context needed to implement this feature independently. Read the linked files, follow the patterns, and deliver high-quality code with tests.
