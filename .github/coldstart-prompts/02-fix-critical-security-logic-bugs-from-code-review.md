# Coldstart Implementation Prompt: Fix Critical Security & Logic Bugs from Code Review

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

Fix Critical Security & Logic Bugs from Code Review

**Priority**: P0 (Critical - Security & Correctness)

**Description**: Address critical bugs discovered in code review that affect security and assessment accuracy.

**Issues to Fix**:

1. **XSS Vulnerability in HTML Reports** (CRITICAL - Security)
   - **Location**: `src/agentready/templates/report.html.j2:579`
   - **Problem**: `assessment_json|safe` disables autoescaping for JSON embedded in JavaScript
   - **Risk**: Repository names, commit messages, file paths from git could contain malicious content
   - **Fix**: Replace with `JSON.parse({{ assessment_json|tojson }})`
   - **Add**: Content Security Policy headers to HTML reports

2. **StandardLayoutAssessor Logic Bug** (CRITICAL - Incorrect Scoring)
   - **Location**: `src/agentready/assessors/structure.py:48`
   - **Problem**: `(repository.path / "tests") or (repository.path / "test")` always evaluates to first path
   - **Impact**: Projects with `test/` instead of `tests/` scored incorrectly
   - **Fix**: Check both paths properly:
     ```python
     tests_path = repository.path / "tests"
     if not tests_path.exists():
         tests_path = repository.path / "test"
     has_tests = tests_path.exists()
     ```

**Implementation**:

**File 1**: `src/agentready/templates/report.html.j2`
```jinja2
<!-- BEFORE (VULNERABLE): -->
const ASSESSMENT = {{ assessment_json|safe }};

<!-- AFTER (SECURE): -->
const ASSESSMENT = JSON.parse({{ assessment_json|tojson }});
```

**File 2**: `src/agentready/assessors/structure.py`
```python
# BEFORE (BUGGY):
standard_dirs = {
    "src": repository.path / "src",
    "tests": (repository.path / "tests") or (repository.path / "test"),  # BUG!
}

# AFTER (CORRECT):
standard_dirs = {
    "src": repository.path / "src",
}

# Check for tests directory (either tests/ or test/)
tests_path = repository.path / "tests"
if not tests_path.exists():
    tests_path = repository.path / "test"
standard_dirs["tests"] = tests_path
```

**Test Cases to Add**:
```python
def test_xss_in_repository_name():
    """Test that malicious repo names are escaped in HTML."""
    repo = Repository(
        name="<script>alert('xss')</script>",
        # ...
    )
    html = HTMLReporter().generate(assessment, output)
    assert "<script>" not in html  # Should be escaped

def test_standard_layout_with_test_dir():
    """Test that 'test/' directory is recognized (not just 'tests/')."""
    # Create repo with test/ directory only
    repo_path = tmp_path / "repo"
    (repo_path / "test").mkdir(parents=True)

    assessor = StandardLayoutAssessor()
    finding = assessor.assess(Repository(...))
    assert finding.status == "pass"  # Should recognize test/ dir
```

**Acceptance Criteria**:
- [ ] XSS vulnerability patched with `tojson` filter
- [ ] CSP headers added to HTML reports (future)
- [ ] StandardLayoutAssessor recognizes both `tests/` and `test/`
- [ ] Tests added for XSS prevention
- [ ] Tests added for both test directory naming patterns
- [ ] All existing tests still pass

**Priority Justification**:
- **Security**: XSS is a P0 vulnerability
- **Correctness**: Incorrect scoring undermines tool credibility
- **Quick fixes**: Both are 5-10 minute changes

**Related**: Issue #2 (Report improvements), Bootstrap (#1 - needs secure reports)

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
git checkout -b 002-fix-critical-security-&-logic-bugs-from-code-revie

# Start implementing!
```

---

**Note**: This is a coldstart prompt. You have all context needed to implement this feature independently. Read the linked files, follow the patterns, and deliver high-quality code with tests.
