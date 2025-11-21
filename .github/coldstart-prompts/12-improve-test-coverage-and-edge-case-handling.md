# Coldstart Implementation Prompt: Improve Test Coverage and Edge Case Handling

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

Improve Test Coverage and Edge Case Handling

**Priority**: P1 (High - Quality Assurance)

**Description**: Increase test coverage from 37% to >80% and add tests for critical edge cases discovered in code review.

**Critical Test Gaps**:

1. **Error Handling Paths** (Currently 0% coverage)
   - OSError, PermissionError in file operations
   - MissingToolError in assessors
   - Invalid repository paths
   - Malformed git repositories

2. **Edge Cases** (No tests)
   - Empty repositories
   - Binary files instead of text
   - Symlinks in repository
   - Very large repositories (>10k files)
   - Repositories with `test/` vs `tests/` directories

3. **Security Test Cases**
   - XSS in repository names, commit messages
   - Path traversal attempts
   - Malicious file names

4. **Scorer Edge Cases**
   - All attributes skipped (score should be 0.0)
   - Config weights don't sum to 1.0
   - Division by zero scenarios

**Implementation**:
```python
# tests/unit/test_edge_cases.py
def test_empty_repository(tmp_path):
    """Test assessment of completely empty repository."""
    # Create empty git repo
    repo = Repository(path=tmp_path, ...)
    scanner = Scanner(repo, config=None)
    assessment = scanner.scan(assessors)
    # Should not crash, should have valid score
    assert 0.0 <= assessment.overall_score <= 100.0

def test_permission_denied_file(tmp_path):
    """Test graceful handling of permission errors."""
    # Create unreadable file
    restricted = tmp_path / "CLAUDE.md"
    restricted.write_text("test")
    restricted.chmod(0o000)

    assessor = CLAUDEmdAssessor()
    finding = assessor.assess(Repository(...))
    assert finding.status == "error"
    assert "permission" in finding.error_message.lower()

def test_binary_file_as_readme(tmp_path):
    """Test handling of binary files."""
    readme = tmp_path / "README.md"
    readme.write_bytes(b"\x00\x01\x02\x03")

    assessor = READMEAssessor()
    finding = assessor.assess(Repository(...))
    # Should not crash
```

**Acceptance Criteria**:
- [ ] Test coverage increased to >80%
- [ ] All error handling paths tested
- [ ] Edge cases for empty/malformed repos covered
- [ ] Security test cases added
- [ ] Integration tests for complete workflows
- [ ] CI runs coverage report and fails <75%

**Priority Justification**: Quality assessment tool must be thoroughly tested. Current 37% coverage is unacceptable.

**Related**: CI/CD improvements, reliability

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
git checkout -b 012-improve-test-coverage-and-edge-case-handling

# Start implementing!
```

---

**Note**: This is a coldstart prompt. You have all context needed to implement this feature independently. Read the linked files, follow the patterns, and deliver high-quality code with tests.
