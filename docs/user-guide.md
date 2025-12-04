---
layout: page
title: User Guide
---

Complete guide to installing, configuring, and using AgentReady to assess your repositories.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Bootstrap Your Repository](#bootstrap-your-repository) ⭐ **NEW**
  - [What is Bootstrap?](#what-is-bootstrap)
  - [When to Use Bootstrap vs Assess](#when-to-use-bootstrap-vs-assess)
  - [Quick Tutorial](#quick-tutorial)
- [Align Command](#align-command)
- [Running Assessments](#running-assessments)
- [Understanding Reports](#understanding-reports)
- [Configuration](#configuration)
- [CLI Reference](#cli-reference)
- [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- **Python 3.12 or 3.13** (AgentReady supports versions N and N-1)
- **Git** (for repository analysis)
- **pip** or **uv** (Python package manager)

### Install from PyPI

```bash
# Using pip
pip install agentready

# Using uv (recommended)
uv pip install agentready

# Verify installation
agentready --version
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/ambient-code/agentready.git
cd agentready

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Or using uv
uv pip install -e .
```

### Development Installation

If you plan to contribute or modify AgentReady:

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or using uv
uv pip install -e ".[dev]"

# Verify installation
pytest --version
black --version
```

---

## Quick Start

### Bootstrap-First Approach (Recommended)

Transform your repository with one command:

```bash
# Navigate to your repository
cd /path/to/your/repo

# Bootstrap infrastructure
agentready bootstrap .

# Review generated files
git status

# Commit and push
git add .
git commit -m "build: Bootstrap agent-ready infrastructure"
git push
```

**What happens:**

- ✅ GitHub Actions workflows created (tests, security, assessment)
- ✅ Pre-commit hooks configured
- ✅ Issue/PR templates added
- ✅ Dependabot enabled
- ✅ Assessment runs automatically on next PR

**Duration**: <60 seconds including review time.

[See detailed Bootstrap tutorial →](#bootstrap-your-repository)

### Batch Assessment Approach

Assess multiple repositories at once for organizational insights:

```bash
# Navigate to directory containing multiple repos
cd /path/to/repos

# Run batch assessment
agentready batch repo1/ repo2/ repo3/ --output-dir ./batch-reports

# View comparison report
open batch-reports/comparison-summary.html
```

**What you get:**

- ✅ Individual reports for each repository
- ✅ Comparison table showing scores side-by-side
- ✅ Aggregate statistics across all repositories
- ✅ Trend analysis for multi-repo projects

**Duration**: Varies by number of repositories (~5 seconds per repo).

[See detailed batch assessment guide →](#batch-assessment)

### Manual Assessment Approach

For one-time analysis without infrastructure changes:

```bash
# Navigate to your repository
cd /path/to/your/repo

# Run assessment
agentready assess .

# View the HTML report
open .agentready/report-latest.html  # macOS
xdg-open .agentready/report-latest.html  # Linux
start .agentready/report-latest.html  # Windows
```

**Output location**: `.agentready/` directory in your repository root.

**Duration**: Most assessments complete in under 5 seconds.

---

## Bootstrap Your Repository

### What is Bootstrap?

Bootstrap automatically generates complete GitHub infrastructure in one command instead of manually implementing assessment recommendations. Generated files include GitHub Actions workflows (tests, security, assessment), pre-commit hooks (language-specific formatters/linters), issue/PR templates, CODEOWNERS for review assignments, Dependabot for weekly updates, and contributing guidelines with Code of Conduct if missing.

Bootstrap detects your primary language (Python, JavaScript, Go) via `git ls-files` and generates appropriate configurations. Use `--dry-run` to preview changes without creating files - all files are created never overwritten, so review with `git status` before committing.

---

### When to Use Bootstrap vs Assess

<table>
<thead>
<tr>
<th>Scenario</th>
<th>Use Bootstrap</th>
<th>Use Assess</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>New project</strong></td>
<td>✅ Start with best practices</td>
<td>Later, to track progress</td>
</tr>
<tr>
<td><strong>Missing GitHub Actions</strong></td>
<td>✅ Generate workflows instantly</td>
<td>Shows it's missing</td>
</tr>
<tr>
<td><strong>No pre-commit hooks</strong></td>
<td>✅ Configure automatically</td>
<td>Shows it's missing</td>
</tr>
<tr>
<td><strong>Understanding current state</strong></td>
<td>Use after bootstrapping</td>
<td>✅ Detailed analysis</td>
</tr>
<tr>
<td><strong>Existing infrastructure</strong></td>
<td>Safe (won't overwrite)</td>
<td>✅ Validate setup</td>
</tr>
<tr>
<td><strong>Tracking improvements</strong></td>
<td>One-time setup</td>
<td>✅ Run repeatedly</td>
</tr>
<tr>
<td><strong>CI/CD integration</strong></td>
<td>Generates the workflows</td>
<td>✅ Runs in CI (via Bootstrap)</td>
</tr>
</tbody>
</table>

**Recommended workflow**: Bootstrap first to generate infrastructure, review and commit generated files, assess automatically on every PR via GitHub Actions, and run manual assessments when validating improvements.

---

### Quick Tutorial

Start with dry-run to preview changes: `agentready bootstrap . --dry-run` detects your primary language and lists files to be created (workflows, templates, hooks). Files marked "(not present, will create)" are new - existing files are never overwritten.

Run `agentready bootstrap .` to create infrastructure. Bootstrap generates 10-15 files including GitHub Actions workflows (tests, security, assessment), pre-commit config, issue/PR templates, CODEOWNERS, and Dependabot config. Review generated files with `git status` and customize CODEOWNERS (add actual usernames), workflow triggers (adjust branches/paths), and pre-commit hooks (add/remove tools).

Install hooks locally with `pip install pre-commit && pre-commit install && pre-commit run --all-files`. If hooks fail, run formatters (`black . && isort .`) and linters (`ruff check . --fix`) then re-run hooks.

Commit with `git add . && git commit -m "build: Bootstrap agent-ready infrastructure"` and push to remote. Enable GitHub Actions in Settings → Actions → General (select "Allow all actions" and "Read and write permissions"). Test by creating a PR - the assessment workflow runs automatically and posts results as a comment showing your score, tier breakdown, and link to full HTML report.

---

### Generated Files

Bootstrap generates three GitHub Actions workflows: `agentready-assessment.yml` runs on every PR/push posting results as comments and failing if score drops below threshold (default 60), `tests.yml` runs language-specific tests with coverage (pytest for Python, jest for JavaScript, go test for Go), and `security.yml` runs CodeQL vulnerability analysis plus dependency scanning that fails on high/critical issues.

---

Pre-commit hooks include language-specific formatters and linters: Python (black, isort, ruff), JavaScript/TypeScript (prettier, eslint), Go (gofmt, golint, go-vet), plus trailing-whitespace and end-of-file fixers for all languages. Customize by editing `.pre-commit-config.yaml` to adjust versions or add repos.

---

Issue templates include structured bug reports (with reproduction steps, environment details, auto-labeled as `bug`) and feature requests (with use case, motivation, auto-labeled as `enhancement`). PR template provides author checklist (tests added, docs updated, checks passed, breaking changes documented). CODEOWNERS auto-assigns reviewers by file path (customize with actual usernames). Dependabot creates weekly PRs for outdated dependencies (supports Python/npm/Go). CONTRIBUTING.md and CODE_OF_CONDUCT.md are created if missing.

---

### Post-Bootstrap Steps

Edit CODEOWNERS to replace placeholder usernames with actual team members. Review workflow triggers in `.github/workflows/*.yml` and adjust branches (main vs master), path filters, or schedules as needed. Install hooks locally with `pip install pre-commit && pre-commit install && pre-commit run --all-files`.

Enable GitHub Actions in Settings → Actions → General (select "Allow all actions" and "Read and write permissions"). Configure branch protection for main branch requiring status checks (tests, security, agentready-assessment) and PR reviews. Test by creating a PR to verify all workflows run and assessment posts results.

Bootstrap generates language-specific configurations: Python (pytest workflow, black/isort/ruff hooks, Dependabot for pip), JavaScript/TypeScript (jest/npm test workflow, prettier/eslint hooks, Dependabot for npm), Go (go test with race detection, gofmt/golint/go-vet hooks, Dependabot for Go modules). Customize test commands, formatter configs, and add type checking or coverage reporting as needed.

---

### Bootstrap Command Reference

```bash
agentready bootstrap [REPOSITORY] [OPTIONS]
```

**Arguments:**

- `REPOSITORY` — Path to repository (default: current directory)

**Options:**

- `--dry-run` — Preview files without creating
- `--language TEXT` — Override auto-detection: `python|javascript|go|auto` (default: auto)

**Examples:**

```bash
# Bootstrap current directory (auto-detect language)
agentready bootstrap .

# Preview without creating files
agentready bootstrap . --dry-run

# Force Python configuration
agentready bootstrap . --language python

# Bootstrap different directory
agentready bootstrap /path/to/repo

# Combine dry-run and language override
agentready bootstrap /path/to/repo --dry-run --language go
```

**Exit codes:**

- `0` — Success
- `1` — Error (not a git repository, permission denied, etc.)

---

## Align Command

AgentReady Align automatically fixes failing attributes by analyzing your assessment results and applying code generation, file creation, and configuration updates. Run `agentready align .` after your first assessment to immediately improve your score.

The command runs a fresh assessment, identifies all failing attributes with available fixers, calculates projected score improvement, and lets you preview or apply changes. Use `--dry-run` to see what would change without modifying files, or `--interactive` to approve each fix individually.

```bash
# Preview fixes without applying
agentready align . --dry-run

# Apply all available fixes
agentready align .

# Interactively approve each fix
agentready align . --interactive

# Fix specific attributes only
agentready align . --attributes claude_md_file,gitignore_completeness
```

Current fixers handle CLAUDE.md generation (creates comprehensive project documentation using template), .gitignore completion (adds language-specific patterns for Python/JS/Go), pre-commit hook configuration (sets up black/isort/ruff), and README structure enhancement (adds missing essential sections). The projected score shows what you'd achieve if all fixes succeed - typically +15 to +30 points depending on your current state.

After running align, review changes with `git status`, test locally, then commit with `git add . && git commit -m "chore: apply AgentReady fixes"`. Run `agentready assess .` again to verify your new score and identify remaining manual improvements.

---

## Running Assessments

### Basic Usage

```bash
# Assess current directory
agentready assess .

# Assess specific repository
agentready assess /path/to/repo

# Assess with verbose output
agentready assess . --verbose

# Custom output directory
agentready assess . --output-dir ./custom-reports
```

### Assessment Output

AgentReady creates a `.agentready/` directory containing:

```
.agentready/
├── assessment-YYYYMMDD-HHMMSS.json    # Machine-readable data
├── report-YYYYMMDD-HHMMSS.html        # Interactive web report
├── report-YYYYMMDD-HHMMSS.md          # Markdown report
├── assessment-latest.json             # Symlink to latest
├── report-latest.html                 # Symlink to latest
└── report-latest.md                   # Symlink to latest
```

**Timestamps**: All files are timestamped for historical tracking.

**Latest links**: Symlinks always point to the most recent assessment.

### Verbose Mode

Get detailed progress information during assessment:

```bash
agentready assess . --verbose
```

**Output includes**:

- Repository path and detected languages
- Each assessor's execution status
- Finding summaries (pass/fail/skip)
- Final score calculation breakdown
- Report generation progress

---

## Batch Assessment

Assess multiple repositories in one command to gain organizational insights and identify patterns across projects.

### Basic Usage

```bash
# Assess all repos in a directory
agentready batch /path/to/repos --output-dir ./reports

# Assess specific repos
agentready batch /path/repo1 /path/repo2 /path/repo3

# Generate comparison report
agentready batch . --compare
```

### Batch Output

AgentReady batch assessment creates:

```
reports/
├── comparison-summary.html      # Interactive comparison table
├── comparison-summary.md        # Markdown summary
├── aggregate-stats.json         # Machine-readable statistics
├── repo1/
│   ├── assessment-latest.json
│   ├── report-latest.html
│   └── report-latest.md
├── repo2/
│   └── ...
└── repo3/
    └── ...
```

### Comparison Report Features

**comparison-summary.html** includes:

- Side-by-side score comparison table
- Certification level distribution (Platinum/Gold/Silver/Bronze)
- Average scores by tier
- Outlier detection (repos significantly above/below average)
- Sortable columns (by score, name, certification)
- Filterable view (show only failing repos)

**Example comparison table:**

| Repository | Overall Score | Cert Level | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|------------|---------------|------------|--------|--------|--------|--------|
| agentready | 80.0/100 | Gold | 90.0 | 75.0 | 70.0 | 60.0 |
| project-a | 75.2/100 | Gold | 85.0 | 70.0 | 65.0 | 55.0 |
| project-b | 62.5/100 | Silver | 70.0 | 60.0 | 55.0 | 45.0 |

### Aggregate Statistics

**aggregate-stats.json** provides:

```json
{
  "total_repositories": 3,
  "average_score": 72.6,
  "median_score": 75.2,
  "certification_distribution": {
    "Platinum": 0,
    "Gold": 2,
    "Silver": 1,
    "Bronze": 0,
    "Needs Improvement": 0
  },
  "tier_averages": {
    "tier_1": 81.7,
    "tier_2": 68.3,
    "tier_3": 63.3,
    "tier_4": 53.3
  },
  "common_failures": [
    {"attribute": "pre_commit_hooks", "failure_rate": 0.67},
    {"attribute": "lock_files", "failure_rate": 0.33}
  ]
}
```

### Use Cases

**Organization-wide assessment**:

```bash
# Clone all org repos, then batch assess
gh repo list myorg --limit 100 --json name --jq '.[].name' | \
  xargs -I {} gh repo clone myorg/{}

agentready batch repos/* --output-dir ./org-assessment
```

**Multi-repo project**:

```bash
# Assess all microservices
agentready batch services/* --compare
```

**Trend tracking**:

```bash
# Monthly assessment
agentready batch repos/* --output-dir ./assessments/2025-11
```

---

## Report Validation & Migration

AgentReady v1.27.2 includes schema versioning for backwards compatibility and evolution.

### Validate Reports

Verify assessment reports conform to their schema version:

```bash
# Strict validation (default)
agentready validate-report .agentready/assessment-latest.json

# Lenient validation (allow extra fields)
agentready validate-report --no-strict .agentready/assessment-latest.json
```

**Output examples:**

**Valid report:**

```
✅ Report is valid!
Schema version: 1.0.0
Repository: agentready
Overall score: 80.0/100
```

**Invalid report:**

```
❌ Validation failed! 3 errors found:
  - Missing required field: 'schema_version'
  - Invalid type for 'overall_score': expected number, got string
  - Extra field not allowed in strict mode: 'custom_field'
```

### Migrate Reports

Convert reports between schema versions:

```bash
# Migrate to specific version
agentready migrate-report old-report.json --to 2.0.0

# Custom output path
agentready migrate-report old.json --to 2.0.0 --output new.json

# Explicit source version (auto-detected by default)
agentready migrate-report old.json --from 1.0.0 --to 2.0.0
```

**Migration output:**

```
🔄 Migrating report...
Source version: 1.0.0
Target version: 2.0.0

✅ Migration successful!
Migrated report saved to: assessment-20251123-migrated.json
```

### Schema Compatibility

**Current schema version**: 1.0.0

**Supported versions**:

- 1.0.0 (current)

**Future versions** will maintain backwards compatibility:

- Read old versions via migration
- Write new versions with latest schema
- Migration paths provided for all versions

[Learn more about schema versioning →](schema-versioning.html)

---

## Understanding Reports

AgentReady generates three complementary report formats.

### HTML Report (Interactive)

**File**: `report-YYYYMMDD-HHMMSS.html`

The HTML report provides an interactive, visual interface:

#### Features

- **Overall Score Card**: Certification level, score, and visual gauge
- **Tier Summary**: Breakdown by attribute tier (Essential/Critical/Important/Advanced)
- **Attribute Table**: Sortable, filterable list of all attributes
- **Detailed Findings**: Expandable sections for each attribute
- **Search**: Find specific attributes by name or ID
- **Filters**: Show only passed, failed, or skipped attributes
- **Copy Buttons**: One-click code example copying
- **Offline**: No CDN dependencies, works anywhere

#### How to Use

1. **Open in browser**: Double-click the HTML file
2. **Review overall score**: Check certification level and tier breakdown
3. **Explore findings**:
   - Green ✅ = Passed
   - Red ❌ = Failed (needs remediation)
   - Gray ⊘ = Skipped (not applicable or not yet implemented)
4. **Click to expand**: View detailed evidence and remediation steps
5. **Filter results**: Focus on specific attribute statuses
6. **Copy remediation commands**: Use one-click copy for code examples

#### Security

HTML reports include Content Security Policy (CSP) headers for defense-in-depth:

- Prevents unauthorized script execution
- Mitigates XSS attack vectors
- Safe to share and view in any browser

The CSP policy allows only inline styles and scripts needed for interactivity.

#### Sharing

The HTML report is self-contained and can be:

- Emailed to stakeholders
- Uploaded to internal wikis
- Viewed on any device with a browser
- Archived for compliance/audit purposes

### Markdown Report (Version Control Friendly)

**File**: `report-YYYYMMDD-HHMMSS.md`

The Markdown report is optimized for git tracking:

#### Features

- **GitHub-Flavored Markdown**: Renders beautifully on GitHub
- **Git-Diffable**: Track score improvements over time
- **ASCII Tables**: Attribute summaries without HTML
- **Emoji Indicators**: ✅❌⊘ for visual status
- **Certification Ladder**: Visual progress chart
- **Prioritized Next Steps**: Highest-impact improvements first

#### How to Use

1. **Commit to repository**:

   ```bash
   git add .agentready/report-latest.md
   git commit -m "docs: Add AgentReady assessment report"
   ```

2. **Track progress**:

   ```bash
   # Run new assessment
   agentready assess .

   # Compare to previous
   git diff .agentready/report-latest.md
   ```

3. **Review on GitHub**: Push and view formatted Markdown

4. **Share in PRs**: Reference in pull request descriptions

#### Recommended Workflow

```bash
# Initial baseline
agentready assess .
git add .agentready/report-latest.md
git commit -m "docs: AgentReady baseline (Score: 65.2)"

# Make improvements
# ... implement recommendations ...

# Re-assess
agentready assess .
git add .agentready/report-latest.md
git commit -m "docs: AgentReady improvements (Score: 72.8, +7.6)"
```

### JSON Report (Machine-Readable)

**File**: `assessment-YYYYMMDD-HHMMSS.json`

The JSON report contains complete assessment data:

#### Structure

```json
{
  "metadata": {
    "timestamp": "2025-11-21T10:30:00Z",
    "repository_path": "/path/to/repo",
    "agentready_version": "1.0.0",
    "duration_seconds": 2.35
  },
  "repository": {
    "path": "/path/to/repo",
    "name": "myproject",
    "languages": {"Python": 42, "JavaScript": 18}
  },
  "overall_score": 75.4,
  "certification_level": "Gold",
  "tier_scores": {
    "tier_1": 85.0,
    "tier_2": 70.0,
    "tier_3": 65.0,
    "tier_4": 50.0
  },
  "findings": [
    {
      "attribute_id": "claude_md_file",
      "attribute_name": "CLAUDE.md File",
      "tier": 1,
      "weight": 0.10,
      "status": "pass",
      "score": 100,
      "evidence": "Found CLAUDE.md at repository root",
      "remediation": null
    }
  ]
}
```

#### Use Cases

**CI/CD Integration**:

```bash
# Fail build if score < 70
score=$(jq '.overall_score' .agentready/assessment-latest.json)
if (( $(echo "$score < 70" | bc -l) )); then
  echo "AgentReady score too low: $score"
  exit 1
fi
```

**Trend Analysis**:

```python
import json
import glob

# Load all historical assessments
assessments = []
for file in sorted(glob.glob('.agentready/assessment-*.json')):
    with open(file) as f:
        assessments.append(json.load(f))

# Track score over time
for a in assessments:
    print(f"{a['metadata']['timestamp']}: {a['overall_score']}")
```

**Custom Reporting**:

```python
import json

with open('.agentready/assessment-latest.json') as f:
    assessment = json.load(f)

# Extract failed attributes
failed = [
    f for f in assessment['findings']
    if f['status'] == 'fail'
]

# Create custom report
for finding in failed:
    print(f"❌ {finding['attribute_name']}")
    print(f"   {finding['evidence']}")
    print()
```

---

## Configuration

### Default Behavior

AgentReady works out-of-the-box with sensible defaults. No configuration required for basic usage.

### Custom Configuration File

Create `.agentready-config.yaml` to customize:

```yaml
# Custom attribute weights (must sum to 1.0)
weights:
  claude_md_file: 0.15      # Increase from default 0.10
  readme_structure: 0.12    # Increase from default 0.10
  type_annotations: 0.08    # Decrease from default 0.10
  # ... other 22 attributes

# Exclude specific attributes
excluded_attributes:
  - performance_benchmarks  # Skip this assessment
  - container_setup         # Not applicable to our project

# Custom output directory
output_dir: ./reports

# Verbosity (true/false)
verbose: false
```

### Weight Customization Rules

1. **Must sum to 1.0**: Total weight across all attributes (excluding excluded ones)
2. **Minimum weight**: 0.01 (1%)
3. **Maximum weight**: 0.20 (20%)
4. **Automatic rebalancing**: Excluded attributes' weights redistribute proportionally

### Example: Security-Focused Configuration

```yaml
# Emphasize security attributes
weights:
  dependency_security: 0.15    # Default: 0.05
  secrets_management: 0.12     # Default: 0.05
  security_scanning: 0.10      # Default: 0.03
  # Other weights adjusted to sum to 1.0

excluded_attributes:
  - performance_benchmarks
```

### Example: Documentation-Focused Configuration

```yaml
# Emphasize documentation quality
weights:
  claude_md_file: 0.20         # Default: 0.10
  readme_structure: 0.15       # Default: 0.10
  inline_documentation: 0.12   # Default: 0.08
  api_documentation: 0.10      # Default: 0.05
  # Other weights adjusted to sum to 1.0
```

### Validate Configuration

```bash
# Validate configuration file
agentready --validate-config .agentready-config.yaml

# Generate example configuration
agentready --generate-config > .agentready-config.yaml
```

---

## CLI Reference

### Main Commands

#### `agentready assess PATH`

Assess a repository at the specified path.

**Arguments**:

- `PATH` — Repository path to assess (required)

**Options**:

- `--verbose, -v` — Show detailed progress information
- `--config FILE, -c FILE` — Use custom configuration file
- `--output-dir DIR, -o DIR` — Custom report output directory

**Examples**:

```bash
agentready assess .
agentready assess /path/to/repo
agentready assess . --verbose
agentready assess . --config custom.yaml
agentready assess . --output-dir ./reports
```

### Configuration Commands

#### `agentready --generate-config`

Generate example configuration file.

**Output**: Prints YAML configuration to stdout.

**Example**:

```bash
agentready --generate-config > .agentready-config.yaml
```

#### `agentready --validate-config FILE`

Validate configuration file syntax and weights.

**Example**:

```bash
agentready --validate-config .agentready-config.yaml
```

### Research Commands

#### `agentready --research-version`

Show bundled research document version.

**Example**:

```bash
agentready --research-version
# Output: Research version: 1.0.0 (2025-11-20)
```

### Utility Commands

#### `agentready --version`

Show AgentReady version.

#### `agentready --help`

Show help message with all commands.

---

## Troubleshooting

### Common Issues

**"No module named 'agentready'"**: Verify Python version (should be 3.12 or 3.13), check installation with `pip list | grep agentready`, reinstall if missing with `pip install agentready`.

**"Permission denied: .agentready/"**: Use custom output directory `agentready assess . --output-dir ~/agentready-reports` or fix permissions with `chmod u+w .`.

**"Repository not found"**: Verify with `git status`. If not a git repo, initialize with `git init`.

**"Assessment taking too long"**: Should complete in <10 seconds. If it hangs, check verbose output `agentready assess . --verbose` and verify git performance with `time git ls-files`. AgentReady warns before scanning repositories with >10,000 files.

**"Warning: Scanning sensitive directory"**: Safety check prevents scanning system directories (/etc, /sys, /proc, /.ssh, /var). Only scan project repositories - copy from /var/www to user directory if needed, use `--output-dir` to avoid writing to sensitive locations.

**"Invalid configuration file"**: Malformed YAML or incorrect weights. Solution:

```bash
# Validate configuration
agentready --validate-config .agentready-config.yaml

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('.agentready-config.yaml'))"

# Regenerate from template
agentready --generate-config > .agentready-config.yaml
```

---

### Bootstrap-Specific Issues

#### "File already exists" error

**Cause**: Bootstrap refuses to overwrite existing files.

**Solution**:
Bootstrap is safe by design—it never overwrites existing files. This is expected behavior:

```bash
# Review what files already exist
ls -la .github/workflows/
ls -la .pre-commit-config.yaml

# If you want to regenerate, manually remove first
rm .github/workflows/agentready-assessment.yml
agentready bootstrap .

# Or keep existing and only add missing files
agentready bootstrap .  # Safely skips existing
```

---

#### "Language detection failed"

**Cause**: No recognizable language files in repository.

**Solution**:

```bash
# Check what files git tracks
git ls-files

# If empty, add some files first
git add *.py  # or *.js, *.go

# Force specific language
agentready bootstrap . --language python

# Or if mixed language project
agentready bootstrap . --language auto  # Uses majority language
```

---

#### "GitHub Actions not running"

**Cause**: Actions not enabled or insufficient permissions.

**Solution**:

1. **Enable Actions**:
   - Repository Settings → Actions → General
   - Select "Allow all actions"
   - Save

2. **Check workflow permissions**:
   - Settings → Actions → General → Workflow permissions
   - Select "Read and write permissions"
   - Save

3. **Verify workflow files**:

   ```bash
   # Check files were created
   ls -la .github/workflows/

   # Validate YAML syntax
   cat .github/workflows/agentready-assessment.yml
   ```

4. **Trigger manually**:
   - Actions tab → Select workflow → "Run workflow"

---

#### "Pre-commit hooks not running"

**Cause**: Hooks not installed locally.

**Solution**:

```bash
# Install pre-commit framework
pip install pre-commit

# Install git hooks
pre-commit install

# Verify installation
ls -la .git/hooks/
# Should see pre-commit file

# Test hooks
pre-commit run --all-files
```

**If hooks fail:**

```bash
# Update hook versions
pre-commit autoupdate

# Clear cache
pre-commit clean

# Reinstall
pre-commit uninstall
pre-commit install
```

---

#### "Dependabot PRs not appearing"

**Cause**: Dependabot not enabled for repository or incorrect config.

**Solution**:

1. **Check Dependabot is enabled**:
   - Repository Settings → Security & analysis
   - Enable "Dependabot alerts" and "Dependabot security updates"

2. **Verify config**:

   ```bash
   cat .github/dependabot.yml

   # Should have correct package-ecosystem:
   # - pip (for Python)
   # - npm (for JavaScript)
   # - gomod (for Go)
   ```

3. **Check for existing dependency issues**:
   - Security tab → Dependabot
   - View pending updates

4. **Manual trigger**:
   - Wait up to 1 week for first scheduled run
   - Or manually trigger via GitHub API

---

#### "CODEOWNERS not assigning reviewers"

**Cause**: Invalid usernames or team names in CODEOWNERS.

**Solution**:

```bash
# Edit CODEOWNERS
vim .github/CODEOWNERS

# Use valid GitHub usernames (check they exist)
* @alice @bob

# Or use teams (requires org ownership)
* @myorg/team-name

# Verify syntax
# Each line: <file pattern> <owner1> <owner2>
*.py @python-experts
/docs/ @documentation-team
```

**Common mistakes:**

- Using email instead of GitHub username
- Typo in username
- Team name without org prefix (@myorg/team)
- Missing @ symbol

---

#### "Assessment workflow failing"

**Cause**: Various potential issues with workflow execution.

**Solution**:

1. **Check workflow logs**:
   - Actions tab → Select failed run → View logs

2. **Common failures**:

   **Python not found:**

   ```yaml
   # In .github/workflows/agentready-assessment.yml
   # Ensure correct Python version
   - uses: actions/setup-python@v4
     with:
       python-version: '3.11'  # Or '3.12'
   ```

   **AgentReady not installing:**

   ```yaml
   # Check pip install step
   - run: pip install agentready

   # Or use specific version
   - run: pip install agentready==1.1.0
   ```

   **Permission denied:**

   ```yaml
   # Add permissions to workflow
   permissions:
     contents: read
     pull-requests: write  # For PR comments
   ```

3. **Test locally**:

   ```bash
   # Run same commands as workflow
   pip install agentready
   agentready assess .
   ```

---

### Report Issues

If you encounter issues not covered here:

1. **Check GitHub Issues**: [github.com/ambient-code/agentready/issues](https://github.com/ambient-code/agentready/issues)
2. **Search Discussions**: Someone may have encountered similar problems
3. **Create New Issue**: Use the bug report template with:
   - AgentReady version (`agentready --version`)
   - Python version (`python --version`)
   - Operating system
   - Complete error message
   - Steps to reproduce

---

## Next Steps

- **[Developer Guide](developer-guide.html)** — Learn how to contribute and extend AgentReady
- **[API Reference](api-reference.html)** — Integrate AgentReady into your tools
- **[Examples](examples.html)** — See real-world assessment reports

---

**Questions?** Join the discussion on [GitHub](https://github.com/ambient-code/agentready/discussions).
