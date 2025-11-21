# Coldstart Implementation Prompt: Create Automated Demo

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

Create Automated Demo

**Priority**: P0 (Critical - Showcase Value)

**Description**: Create an automated, self-contained demonstration of AgentReady that shows the tool assessing a sample repository, generating reports, and providing remediation guidance. This should be runnable with a single command and suitable for demos, presentations, and onboarding.

**Requirements**:
- Single command to run: `agentready demo`
- Self-contained sample repository (embedded in package or generated on-the-fly)
- Demonstrates full workflow:
  1. Repository analysis
  2. Attribute assessment
  3. Score calculation
  4. HTML/Markdown report generation
  5. Remediation suggestions
- Interactive terminal output showing progress
- Opens generated HTML report automatically in browser
- Reusable for presentations and stakeholder demos

**Implementation**:

```bash
# Run automated demo
agentready demo

# Output:
# 🤖 AgentReady Demo
# ===================
#
# Creating sample repository...
# Analyzing structure...
# Running 25 assessments...
#   ✅ claude_md_file (100/100)
#   ❌ precommit_hooks (0/100)
#   ... [progress indicators]
#
# Assessment complete!
# Score: 67.3/100 (Silver)
#
# Generating reports...
#   📄 demo-report.html (generated)
#   📄 demo-report.md (generated)
#   📄 demo-assessment.json (generated)
#
# Opening HTML report in browser...
```

**Sample Repository Options**:

**Option 1: Embedded Examples** (Ship with package)
```
src/agentready/demo/
├── sample-python-repo/      # Python project (minimal)
│   ├── src/myapp/
│   ├── tests/
│   ├── README.md
│   ├── pyproject.toml
│   └── .gitignore
├── sample-js-repo/          # JavaScript project
│   ├── src/
│   ├── package.json
│   └── README.md
└── sample-go-repo/          # Go project
```

**Option 2: Generate On-the-Fly** (Dynamic)
```python
def create_demo_repo(tmp_path: Path, language: str = "python") -> Path:
    """Create sample repository for demo."""
    repo = tmp_path / "demo-repo"
    repo.mkdir()

    if language == "python":
        # Create minimal Python project
        create_file(repo / "README.md", "# Demo Project\n\nSample Python project.")
        create_file(repo / "src/main.py", "def main(): pass")
        create_file(repo / ".gitignore", "*.pyc\n__pycache__/")
        # Missing: CLAUDE.md, tests/, pre-commit hooks (intentional for demo)

    return repo
```

**Demo Script Features**:
- **Progress indicators**: Show assessment running in real-time
- **Color-coded output**: Green for pass, red for fail, yellow for warnings
- **Simulated delays**: Add realistic pauses for "dramatic effect" in demos
- **Narration mode**: Optional verbose output explaining each step
- **Screenshot mode**: Generate high-quality terminal screenshots for docs
- **Record mode**: Save terminal session as GIF/video for presentations

**Configuration**:

```yaml
# Demo config embedded in package
demo:
  sample_repo: python  # or javascript, go, minimal
  show_progress: true
  auto_open_browser: true
  output_dir: ./demo-output
  narration: true  # Explain each step
  delay_ms: 500    # Pause between steps for visibility
```

**Use Cases**:

**Use Case 1: Stakeholder Demo**
```bash
# Quick 2-minute demo for leadership
agentready demo --narration
# Shows: What AgentReady does, how it scores, what reports look like
```

**Use Case 2: Onboarding New Users**
```bash
# Help new users understand the tool
agentready demo --tutorial
# Interactive walkthrough with explanations
```

**Use Case 3: Generate Demo Content for Docs**
```bash
# Create screenshots and videos for documentation
agentready demo --screenshot --record demo.gif
```

**Acceptance Criteria**:
- [ ] `agentready demo` runs without any setup
- [ ] Creates sample repository automatically
- [ ] Runs full assessment workflow
- [ ] Generates all report formats (HTML, Markdown, JSON)
- [ ] Opens HTML report in browser
- [ ] Colorful, engaging terminal output
- [ ] Completes in < 5 seconds
- [ ] No external dependencies required
- [ ] Works offline
- [ ] Includes narration mode for presentations

**Priority Justification**:
- Critical for showcasing tool value to stakeholders
- Needed for Red Hat internal demos and presentations
- Helps with user onboarding and adoption
- Low effort, high impact for visibility
- Required before pitching to other Red Hat teams

**Related**: Onboarding, documentation, marketing

**Notes**:
- Keep demo simple and fast (< 5 seconds)
- Focus on visual impact (colors, progress bars)
- Make it suitable for screenshots/videos
- Consider adding "failure scenario" demo too
- Could expand to multiple language demos
- Add to bootstrap command as part of repo setup

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
git checkout -b 001-create-automated-demo

# Start implementing!
```

---

**Note**: This is a coldstart prompt. You have all context needed to implement this feature independently. Read the linked files, follow the patterns, and deliver high-quality code with tests.
