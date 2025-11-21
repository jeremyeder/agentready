# AgentReady Backlog

**Purpose**: Track future features and improvements for the agentready tool.

---

## Future Features

### Bootstrap New GitHub Repositories

**Priority**: P5 (Future Enhancement)

**Description**: Create functionality to bootstrap new GitHub repositories with agentready tooling and best practices from the start.

**Requirements**:
- Initialize new repository with agent-ready structure
- Create initial CLAUDE.md, README, .gitignore from templates
- Set up pre-commit hooks
- Configure GitHub Actions for agentready assessment
- Set up Dependabot
- Create PR/Issue templates
- Generate initial pyproject.toml or package.json with recommended dependencies

**Use Case**:
```bash
# Bootstrap new repository
agentready init --repo ambient-code/new-project --language python

# This would:
# 1. Create repository structure matching standard layout
# 2. Add CLAUDE.md, README.md, .gitignore templates
# 3. Configure CI/CD with agentready assessment workflow
# 4. Set up development environment configuration
```

**Related**: Initial repository creation, onboarding automation

**Notes**:
- Should support multiple languages (Python, JavaScript, TypeScript, Go, Java)
- Templates should be customizable
- Could integrate with GitHub CLI (gh) for repository creation
- Consider integration with `gh repo create` workflow

---

## Schema & Configuration

### Report Schema Versioning

**Priority**: P3 (Important)

**Description**: Define and version the JSON/HTML/Markdown report schemas to ensure backwards compatibility and enable schema evolution.

**Requirements**:
- JSON schema for assessment reports (contracts/assessment-schema.json exists)
- HTML schema for interactive reports (contracts/report-html-schema.md exists)
- Markdown schema for version control reports (contracts/report-markdown-schema.md exists)
- Schema versioning strategy (semantic versioning)
- Backwards compatibility testing
- Schema migration tools for major version changes

**Use Case**:
```bash
# Validate report against schema
agentready validate-report assessment-2025-11-20.json

# Migrate old report to new schema version
agentready migrate-report --from 1.0.0 --to 2.0.0 old-report.json
```

**Related**: Report generation, data model evolution

**Notes**:
- Schemas exist in contracts/ directory but need formal versioning
- Consider using JSON Schema Draft 2020-12
- Tool should validate generated reports against bundled schema
- Breaking schema changes should trigger major version bump

---

### Research Report Generator/Updater Utility

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

### Repomix Integration

**Priority**: P4 (Enhancement)

**Description**: Integrate with Repomix (https://github.com/yamadashy/repomix) to generate AI-optimized repository context files for both new and existing repositories.

**Requirements**:
- Generate Repomix output for existing repositories
- Include Repomix configuration in bootstrapped new repositories
- Optional GitHub Actions integration for automatic regeneration
- Support Repomix configuration customization
- Integrate with agentready assessment workflow

**Use Case**:
```bash
# Generate Repomix output for current repository
agentready repomix-generate

# Bootstrap new repo with Repomix integration
agentready init --repo my-project --language python --repomix

# This would:
# 1. Set up Repomix configuration
# 2. Add GitHub Action for automatic regeneration
# 3. Generate initial repository context file
# 4. Include Repomix output in .gitignore appropriately
```

**Features**:
- Automatic Repomix configuration based on repository language
- GitHub Actions workflow for CI/CD integration
- Custom ignore patterns aligned with agentready assessment
- Support for both markdown and XML output formats
- Integration with agentready bootstrap command

**Related**: Repository initialization, AI-assisted development workflows

**Notes**:
- Repomix generates optimized repository context for LLMs
- Could enhance CLAUDE.md with reference to Repomix output
- Should align with existing .gitignore patterns
- Consider adding Repomix freshness check to assessment attributes
- May improve agentready's own repository understanding

---

### AgentReady Repository Agent

**Priority**: P3 (Important)

**Description**: Create a specialized Claude Code agent for the AgentReady repository to assist with development, testing, and maintenance tasks.

**Requirements**:
- Agent with deep knowledge of AgentReady architecture
- Understands assessment workflow, scoring logic, and report generation
- Can help with:
  - Implementing new assessors
  - Enhancing existing assessors
  - Writing tests for new features
  - Debugging assessment issues
  - Improving report templates
  - Optimizing performance

**Use Case**:
```bash
# In Claude Code, use the agentready-dev agent
/agentready-dev implement new assessor for dependency security scanning
/agentready-dev debug why Python type annotation detection is failing
/agentready-dev optimize assessment performance for large repositories
```

**Features**:
- Pre-loaded context about AgentReady codebase structure
- Knowledge of assessment attributes and scoring algorithm
- Understanding of tier-based weighting system
- Familiar with reporter implementations (HTML, Markdown)
- Can generate new assessors following established patterns

**Implementation**:
- Create `.claude/agents/agentready-dev.md` with agent specification
- Include links to key design documents (data-model.md, plan.md, research.md)
- Provide common development patterns and examples
- Reference test structure and coverage requirements

**Related**: Development workflow, code generation, testing

**Notes**:
- Agent should follow constitution principles (library-first, TDD when requested)
- Should know about stub assessors and how to expand them
- Can help with performance benchmarking and optimization
- Should understand the research report structure and attribute definitions

---

### Customizable HTML Report Themes

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
- Multiple built-in themes
- Dark mode support
- Custom color palettes
- Font selection (system fonts + web-safe fonts)
- Layout density options (compact, comfortable, spacious)
- Logo/branding customization
- Export theme as reusable configuration

**Implementation**:
- CSS custom properties (variables) for theming
- Theme loader in HTMLReporter
- Validate theme configurations
- Preserve accessibility in all themes
- Add theme preview command: `agentready theme-preview dark`

**Related**: HTML report generation, user experience

**Notes**:
- All themes must maintain WCAG 2.1 AA contrast ratios
- Dark mode should invert appropriately, not just be dark
- Consider colorblind-friendly palettes (Viridis, ColorBrewer)
- Custom themes should be shareable (export/import)
- Could add theme gallery in documentation

---

### Interactive Dashboard with Automated Remediation

**Priority**: P2 (High Value)

**Description**: Transform the static HTML report into an interactive dashboard that enables one-click remediation via automated GitHub issue creation and draft PR generation.

**Vision**: "How to Align Your Repo with Best Practices" - Click a button → Open GitHub issue with draft PR containing fixes.

**Core Features**:

1. **Interactive Dashboard Mode**
   - Real-time assessment (WebSocket updates)
   - Live filtering and sorting (already have this)
   - Action buttons on each failing attribute
   - Progress tracking across multiple runs
   - Historical trend visualization

2. **One-Click Remediation Actions**
   - "Fix This" button on each failing attribute
   - Generates GitHub issue automatically
   - Creates draft PR with proposed changes
   - Links issue to PR
   - Assigns to repository owner/team

3. **Automated Fix Generation**
   - Template-based fixes for common issues:
     - Missing .gitignore → Generate language-specific .gitignore
     - No CLAUDE.md → Generate template with repo analysis
     - Missing pre-commit hooks → Add .pre-commit-config.yaml
     - No lock files → Generate appropriate lock file
     - Missing README sections → Scaffold missing sections
   - AI-powered fixes for complex issues:
     - Refactor high-complexity functions
     - Add type annotations to functions
     - Generate docstrings from function signatures
     - Split large files

4. **GitHub Integration**
   - OAuth authentication with GitHub
   - gh CLI integration for seamless workflow
   - Create issues via GitHub API
   - Create draft PRs via GitHub API
   - Auto-label issues (e.g., `agentready`, `automated-fix`, `tier-1-essential`)
   - Link to AgentReady assessment report

**Technical Architecture**:

```yaml
# New components needed:

Backend (Optional - could be fully client-side with gh CLI):
  - GitHub OAuth app for authentication
  - Issue/PR template generator
  - Fix generator service (template-based + AI-powered)
  - Assessment history tracker

Frontend (Enhanced HTML report):
  - Action buttons with loading states
  - GitHub auth flow UI
  - Progress indicators
  - Toast notifications for actions
  - Modal dialogs for fix preview

CLI Extensions:
  - agentready dashboard .  # Launch local web server
  - agentready fix <attribute-id>  # Generate fix for specific attribute
  - agentready create-issue <attribute-id>  # Create GitHub issue
  - agentready create-pr <attribute-id>  # Create draft PR
```

**Use Cases**:

**Use Case 1: Quick Fixes**
```bash
# User runs assessment
agentready assess . --dashboard

# Opens dashboard in browser at http://localhost:8000
# User clicks "Fix This" on "Missing CLAUDE.md"
# → Creates issue: "Add CLAUDE.md configuration file"
# → Creates draft PR with generated CLAUDE.md template
# → PR includes: project analysis, detected languages, suggested structure
```

**Use Case 2: Batch Remediation**
```bash
# Dashboard shows all failures
# User selects multiple attributes
# Clicks "Fix All Selected"
# → Creates single issue: "Improve AgentReady Score from Silver to Gold"
# → Creates draft PR with all fixes
# → PR description includes before/after score projection
```

**Use Case 3: CI/CD Integration**
```bash
# GitHub Action runs assessment
# Posts comment on PR with assessment results
# Includes links to create remediation issues
# Can auto-create draft PR for improvements
```

**Implementation Approach**:

**Phase 1: Client-Side with gh CLI** (Simplest, no backend needed)
- Use JavaScript in HTML report to call gh CLI via local proxy
- Generate fix files locally
- Use `gh issue create` and `gh pr create`
- Works for users with gh CLI installed

**Phase 2: Dashboard Server** (Enhanced UX)
- Flask/FastAPI server serving dashboard
- WebSocket for live updates
- GitHub OAuth for authentication
- Background workers for fix generation

**Phase 3: Cloud Service** (SaaS offering)
- Hosted dashboard at agentready.dev
- GitHub App installation
- Webhook integration for continuous monitoring
- Team collaboration features

**Fix Templates by Attribute**:

```yaml
claude_md_file:
  type: template
  generates:
    - file: CLAUDE.md
      content: |
        # {repository_name}

        ## Overview
        {auto_generated_description}

        ## Architecture
        {detected_patterns}

        ## Development
        {build_commands}

lock_files:
  type: command
  commands:
    - condition: has_package_json
      run: npm install
    - condition: has_pyproject_toml
      run: poetry lock || pip freeze > requirements.txt

precommit_hooks:
  type: template
  generates:
    - file: .pre-commit-config.yaml
      content: {language_specific_hooks}

readme_structure:
  type: enhancement
  modifies: README.md
  adds_sections:
    - Installation
    - Usage
    - Development
    - Contributing

type_annotations:
  type: ai_powered
  uses: ast_analysis + llm
  modifies: "*.py"
  adds: type_hints
```

**Dashboard vs Report Decision**:

**Keep Both**:
- Static reports for CI/CD, documentation, archiving
- Dashboard for interactive development workflow
- Reports can link to dashboard for remediation
- Dashboard can export static reports

**Benefits of Dashboard**:
- ✅ Interactive remediation workflow
- ✅ Live assessment updates
- ✅ Progress tracking over time
- ✅ Team collaboration (comments, assignments)
- ✅ Automated fix preview before applying
- ✅ Integration with existing tools (GitHub, IDEs)

**Challenges**:
- Authentication complexity (GitHub OAuth)
- Fix generation quality (need good templates + AI)
- PR review overhead (lots of automated PRs)
- Maintaining fix templates as best practices evolve

**Recommended Approach**:

1. **Start with enhanced static report**:
   - Add "Create Issue" buttons that generate gh CLI commands
   - Users copy/paste commands to create issues
   - Include fix templates in issue descriptions

2. **Add local dashboard** (Phase 2):
   - Flask server with WebSocket updates
   - GitHub integration via gh CLI
   - Generate fixes, preview diffs, create PRs

3. **Consider hosted service** (Phase 3+):
   - If adoption is high
   - SaaS model for teams
   - Continuous monitoring and recommendations

**Related**: GitHub integration, automation, remediation, UX

**Notes**:
- This is a MAJOR feature that could become a standalone product
- Consider MVP: "Copy this gh command" buttons in HTML report
- AI-powered fix generation requires careful validation
- Some fixes (like refactoring) need human review
- Could integrate with existing tools (Dependabot, Renovate)
- May want to partner with GitHub for official integration

---

## Backlog Metadata

**Created**: 2025-11-21
**Last Updated**: 2025-11-21
**Total Items**: 7
