# Coldstart Implementation Prompt: Fix Code Quality Issues from Code Review

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

Fix Code Quality Issues from Code Review

**Priority**: P1 (High - Quality & Reliability)

**Description**: Address P1 issues discovered in code review that affect reliability, accuracy, and code quality.

**Issues to Fix**:

1. **TOCTOU (Time-of-Check-Time-of-Use) in File Operations**
   - **Location**: Multiple assessors (`documentation.py:46-50`, `documentation.py:174-191`)
   - **Problem**: Check if file exists, then read in separate operation - file could be deleted in between
   - **Impact**: Crashes instead of graceful degradation
   - **Fix**: Use try-except around file reads instead of existence checks
   ```python
   # BEFORE:
   if claude_md_path.exists():
       size = claude_md_path.stat().st_size

   # AFTER:
   try:
       with open(claude_md_path, "r") as f:
           size = len(f.read())
   except FileNotFoundError:
       return Finding(...status="fail"...)
   except OSError as e:
       return Finding.error(self.attribute, f"Could not read: {e}")
   ```

2. **Inaccurate Type Annotation Detection**
   - **Location**: `src/agentready/assessors/code_quality.py:98-102`
   - **Problem**: Regex-based detection has false positives (string literals, dict literals)
   - **Impact**: Inflated type annotation coverage scores
   - **Fix**: Use AST parsing instead of regex:
   ```python
   import ast
   tree = ast.parse(content)
   for node in ast.walk(tree):
       if isinstance(node, ast.FunctionDef):
           total_functions += 1
           has_annotations = (node.returns is not None or
                            any(arg.annotation for arg in node.args.args))
           if has_annotations:
               typed_functions += 1
   ```

3. **Assessment Validation Semantic Confusion**
   - **Location**: `src/agentready/models/assessment.py:54-59`
   - **Problem**: Field named `attributes_skipped` but includes `error` and `not_applicable` statuses
   - **Impact**: Confusing API, unclear semantics
   - **Fix**: Rename to `attributes_not_assessed` OR add separate counters

**Acceptance Criteria**:
- [ ] All file operations use try-except pattern
- [ ] Type annotation detection uses AST parsing
- [ ] Assessment model fields clearly named
- [ ] Tests added for TOCTOU edge cases
- [ ] Tests added for type annotation false positives
- [ ] Documentation updated

**Priority Justification**: These affect reliability and measurement accuracy - critical for a quality assessment tool.

**Related**: Testing improvements, code quality

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
git checkout -b 011-fix-code-quality-issues-from-code-review

# Start implementing!
```

---

**Note**: This is a coldstart prompt. You have all context needed to implement this feature independently. Read the linked files, follow the patterns, and deliver high-quality code with tests.
