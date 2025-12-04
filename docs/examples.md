---
layout: page
title: Examples
---

Real-world AgentReady assessments demonstrating report formats, interpretation guidance, and remediation patterns.

## Table of Contents

- [AgentReady Self-Assessment](#agentready-self-assessment)
- [Report Interpretation Guide](#report-interpretation-guide)
- [Common Remediation Patterns](#common-remediation-patterns)
- [Integration Examples](#integration-examples)

---

## AgentReady Self-Assessment

AgentReady v1.27.2 scores 80.0/100 (Gold certification). Assessed 19/31 attributes (22 implemented, 9 stubs, 12 not applicable). Tier scores: T1 Essential 85.0/100 (42.5/50 points), T2 Critical 75.0/100 (22.5/30 points), T3 Important 100.0/100 (15.0/15 points), T4 Advanced 0.0/100 (not implemented). Passing 8/10 attributes: CLAUDE.md (482 lines, comprehensive project context), README structure (all essential sections), type annotations (95% coverage), standard src/ layout, 37% test coverage (focused on core logic), complete .gitignore, low cyclomatic complexity (avg 4.2). Failing 2/10 attributes: lock files (intentional for library project), pre-commit hooks (manual black/isort/ruff runs). Path to Platinum (90+): Add pre-commit hooks (+3 points), enforce conventional commits (+1.5 points), expand stub assessors, increase test coverage to 80%+.

---

## Report Interpretation Guide

### Understanding Scores

Certification levels: Platinum (90-100, exemplary), Gold (75-89, highly optimized), Silver (60-74, well-suited), Bronze (40-59, basic compatibility), Needs Improvement (0-39, significant friction). Tier breakdown shows weighted contribution: T1 Essential 50%, T2 Critical 30%, T3 Important 15%, T4 Advanced 5%. Focus improvements on high-tier failures for maximum impact.

### Reading HTML Reports

Overall score card shows certification level, score, and gauge. Tier summary table breaks down scores by attribute tier. Attribute table is sortable/filterable (by status, tier, weight). Click attributes to expand detailed findings with evidence and remediation steps. Use filters to focus on failed attributes needing remediation. Copy buttons provide one-click code example copying. Reports are self-contained (no CDN dependencies) with CSP headers for security.

### Prioritizing Improvements

**Strategy 1 - Maximize Points**: Calculate potential gain as `weight × (100 - current_score)`, sort by gain descending, fix top 3-5 attributes. Example: Missing CLAUDE.md (T1, 10%, score 0) → +10 points; Missing pre-commit (T2, 3%, score 0) → +3 points.

**Strategy 2 - Quick Wins**: <15min fixes include creating CLAUDE.md outline, adding .gitignore from template, creating .env.example. <30min fixes include adding README sections, configuring pre-commit hooks, adding PR/issue templates. <1hr fixes include writing initial tests, adding type hints to key functions, creating ADR template.

**Strategy 3 - Foundational First**: Ensure all T1 attributes pass before T2 (T1 = 50% of score). Missing one T1 attribute (-10 points) hurts more than missing five T4 attributes (-5 points total).

---

## Common Remediation Patterns

### Documentation Gaps

Missing CLAUDE.md, incomplete README, no inline documentation. Solution: Create CLAUDE.md with tech stack/commands/structure sections (15min), enhance README with quick start and code examples (30min), add Google-style docstrings to public functions (ongoing).

### Missing Automation

No pre-commit hooks, no CI/CD, manual testing only. Solution: Install pre-commit framework and configure language-specific hooks (15min), create GitHub Actions workflow for tests and linting (30min), enable Dependabot for automated dependency updates (10min).

### Code Quality Deficits

No type annotations, high cyclomatic complexity, code smells. Solution: Add type hints incrementally with mypy (5 functions per day, focus on public APIs first), reduce complexity by refactoring functions with CC >10 (extract helpers, use early returns), eliminate code smells with pylint (fix critical/high issues first, DRY violations, long functions).

---

## Integration Examples

### GitHub Actions CI

Fail builds if score drops below threshold. Workflow runs assessment on PR/push, checks score threshold (default 60), uploads report as artifact, comments PR with results. Use `jq '.overall_score' .agentready/assessment-latest.json` to extract score, compare with threshold using bc, exit 1 if below threshold.

### Badge in README

Display score badge using shields.io format: `![AgentReady Score](https://img.shields.io/badge/AgentReady-75.4%2F100-gold)`. Update badge via GitHub Actions after each assessment by extracting score and certification level from JSON, running update script to modify README.

### Historical Tracking

Track score improvements over time using Python script: load all `assessment-*.json` files from `.agentready/` directory sorted by timestamp, extract timestamp and overall_score from each, plot trend with matplotlib showing score progression over time.

---

## Next Steps

- **[User Guide](user-guide.html)** — Learn how to run assessments
- **[Developer Guide](developer-guide.html)** — Implement custom assessors
- **[API Reference](api-reference.html)** — Integrate AgentReady programmatically

---

**View full reports**: Check out [`examples/self-assessment/`](https://github.com/ambient-code/agentready/tree/main/examples/self-assessment) in the repository for complete HTML, Markdown, and JSON reports.
