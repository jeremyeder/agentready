# Coldstart Implementation Prompt: Improve HTML Report Design (Font Size & Color Scheme)

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

Improve HTML Report Design (Font Size & Color Scheme)

**Priority**: P0 (Critical - Poor User Experience)

**Description**: Completely redesign HTML report color scheme and increase all font sizes by at least 4 points for readability.

**Problems**:
1. **Color scheme is "hideous"** (user feedback) - current purple gradient doesn't work
2. **Font sizes too small** - hard to read on modern displays
3. **Poor contrast** - some text hard to distinguish

**New Color Scheme** (Dark/Professional):
```css
:root {
  /* Base colors - mostly black, dark blue, purple, white */
  --background: #0a0e27;           /* Almost black with blue tint */
  --surface: #1a1f3a;              /* Dark blue surface */
  --surface-elevated: #252b4a;     /* Slightly lighter surface */

  /* Primary colors */
  --primary: #8b5cf6;              /* Purple (accent) */
  --primary-light: #a78bfa;        /* Light purple */
  --primary-dark: #6d28d9;         /* Dark purple */

  /* Text colors */
  --text-primary: #f8fafc;         /* Almost white */
  --text-secondary: #cbd5e1;       /* Light gray */
  --text-muted: #94a3b8;           /* Muted gray */

  /* Status colors */
  --success: #10b981;              /* Green (pass) */
  --warning: #f59e0b;              /* Amber (warning) */
  --danger: #ef4444;               /* Red (fail) */
  --neutral: #64748b;              /* Gray (skipped) */

  /* UI elements */
  --border: #334155;               /* Dark border */
  --shadow: rgba(0, 0, 0, 0.5);   /* Deep shadows */
}
```

**Font Size Increases** (+4pt minimum):
```css
/* Current → New */
body { font-size: 14px → 18px; }
h1 { font-size: 28px → 36px; }
h2 { font-size: 24px → 30px; }
h3 { font-size: 20px → 26px; }
.score { font-size: 48px → 56px; }
.attribute-name { font-size: 16px → 22px; }
.evidence { font-size: 13px → 17px; }
code { font-size: 13px → 16px; }
```

**Design Mockup**:
```
┌─────────────────────────────────────────────────────┐
│ [Dark navy blue background #1a1f3a]                │
│                                                     │
│  🤖 AgentReady Assessment Report                   │
│  Repository: agentready                            │
│  /Users/jeder/repos/sk/agentready                  │
│  [White text #f8fafc, 18px base font]             │
│                                                     │
├─────────────────────────────────────────────────────┤
│ [Purple accent card #8b5cf6]                       │
│                                                     │
│           75.4 / 100                               │
│           [56px, bold, white]                      │
│           🥇 Gold                                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Implementation Checklist**:
- [ ] Replace gradient backgrounds with dark blue/black
- [ ] Update all font sizes (+4pt minimum)
- [ ] Use purple (#8b5cf6) sparingly as accent color
- [ ] Ensure white text on dark backgrounds (WCAG AA)
- [ ] Update certification level colors
- [ ] Redesign score cards with new scheme
- [ ] Test with colorblind simulators
- [ ] Add light mode as alternative (with same professional palette)

**Before/After Color Comparison**:
```
Current (Problems):
- Purple gradient everywhere: #667eea → #764ba2 ❌
- Small text: 14px base ❌
- Busy, overwhelming ❌

New (Professional):
- Dark blue/black base: #0a0e27, #1a1f3a ✅
- Purple accents only: #8b5cf6 ✅
- Large text: 18px base ✅
- Clean, readable ✅
```

**Acceptance Criteria**:
- ✅ All text easily readable (18px minimum body text)
- ✅ Color scheme uses black, dark blue, purple, white palette
- ✅ High contrast (WCAG 2.1 AA compliant)
- ✅ Professional appearance suitable for Red Hat engineering
- ✅ Purple used as accent, not dominant color

**Related**: HTML report generation, UX, accessibility

**Notes**:
- Current design blocks user adoption (visual issues)
- This is the first thing users see - must be excellent
- Consider adding screenshot to docs after redesign
- Font size critical for presentations and stakeholder reviews

---

## Schema & Configuration


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
git checkout -b 005-improve-html-report-design-(font-size-&-color-sche

# Start implementing!
```

---

**Note**: This is a coldstart prompt. You have all context needed to implement this feature independently. Read the linked files, follow the patterns, and deliver high-quality code with tests.
