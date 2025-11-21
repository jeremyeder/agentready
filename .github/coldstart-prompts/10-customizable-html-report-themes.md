# Coldstart Implementation Prompt: Customizable HTML Report Themes

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

Customizable HTML Report Themes

**Priority**: P4 (Enhancement)

**Description**: Allow users to customize the appearance of HTML reports with themes, color schemes, and layout options.

**Requirements**:
- Theme system for HTML reports
- Pre-built themes (default, dark mode, high contrast, colorblind-friendly)
- Custom theme support via configuration
- Maintain accessibility standards (WCAG 2.1 AA)
- Preview themes before applying

**Use Case**:
```yaml
# .agentready-config.yaml
report_theme: dark  # or 'light', 'high-contrast', 'custom'

custom_theme:
  primary_color: "#2563eb"
  success_color: "#10b981"
  warning_color: "#f59e0b"
  danger_color: "#ef4444"
  background: "#1e293b"
  text: "#e2e8f0"
  font_family: "Inter, sans-serif"
```

**Features**:
- **Theme dropdown in top-right corner of HTML report** (runtime switching)
- **Quick dark/light mode toggle button** (one-click switching between dark and light)
- Multiple built-in themes (light, dark, high-contrast, solarized, dracula)
- Dark mode support with proper color inversion
- Custom color palettes
- Font selection (system fonts + web-safe fonts)
- Layout density options (compact, comfortable, spacious)
- Logo/branding customization
- Export theme as reusable configuration
- Save theme preference to localStorage (persists across reports)

**Implementation**:
- CSS custom properties (variables) for theming
- JavaScript theme switcher in HTML report (no page reload)
- Theme loader in HTMLReporter
- Validate theme configurations
- Preserve accessibility in all themes (WCAG 2.1 AA)
- Add theme preview command: `agentready theme-preview dark`
- Embed all theme CSS in single HTML file (offline-capable)

**Related**: HTML report generation, user experience

**Notes**:
- All themes must maintain WCAG 2.1 AA contrast ratios
- Dark mode should invert appropriately, not just be dark
- Consider colorblind-friendly palettes (Viridis, ColorBrewer)
- Custom themes should be shareable (export/import)
- Could add theme gallery in documentation

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
git checkout -b 010-customizable-html-report-themes

# Start implementing!
```

---

**Note**: This is a coldstart prompt. You have all context needed to implement this feature independently. Read the linked files, follow the patterns, and deliver high-quality code with tests.
