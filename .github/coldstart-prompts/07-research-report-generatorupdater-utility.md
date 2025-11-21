# Coldstart Implementation Prompt: Research Report Generator/Updater Utility

**Priority**: P4
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

Research Report Generator/Updater Utility

**Priority**: P4 (Enhancement)

**Description**: Create a utility tool to help maintain and update the research report (agent-ready-codebase-attributes.md) following the validation schema defined in contracts/research-report-schema.md.

**Requirements**:
- Generate new research reports from templates
- Validate existing reports against schema (contracts/research-report-schema.md)
- Update/add attributes while maintaining schema compliance
- Automatically format citations and references
- Extract tier assignments and metadata
- Verify 25 attributes, 4 tiers, 20+ references
- Check for required sections (Definition, Measurable Criteria, Impact on Agent Behavior)

**Use Case**:
```bash
# Validate existing research report
agentready research validate agent-ready-codebase-attributes.md

# Generate new research report from template
agentready research init --output new-research.md

# Add new attribute to research report
agentready research add-attribute \
  --id "attribute_26" \
  --name "New Attribute" \
  --tier 2 \
  --file research.md

# Update metadata (version, date)
agentready research bump-version --type minor

# Lint and format research report
agentready research format research.md
```

**Features**:
- Schema validation (errors vs warnings per research-report-schema.md)
- Automated metadata header generation (version, date in YAML frontmatter)
- Attribute numbering consistency checks (1.1, 1.2, ..., 15.1)
- Citation deduplication and formatting
- Tier distribution balance warnings
- Category coverage analysis
- Markdown formatting enforcement (consistent structure)
- Reference URL reachability checks

**Related**: Research report maintenance, schema compliance, documentation quality

**Notes**:
- Must follow contracts/research-report-schema.md validation rules
- Should prevent invalid reports from being committed
- Could integrate with pre-commit hooks for research report changes
- Consider CLI commands under `agentready research` subcommand
- Tool should be self-documenting (help users fix validation errors)
- Future: Could use LLMs to help generate attribute descriptions from academic papers

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
git checkout -b 007-research-report-generator/updater-utility

# Start implementing!
```

---

**Note**: This is a coldstart prompt. You have all context needed to implement this feature independently. Read the linked files, follow the patterns, and deliver high-quality code with tests.
