# AgentReady Leaderboard Implementation - Cold Start Prompt

**Version**: 1.0
**Date**: 2025-12-03
**Status**: Ready for implementation
**Estimated Scope**: Medium complexity (4 components, ~600 LOC total)

---

## Executive Summary

Implement a community-driven leaderboard where users submit AgentReady assessment results via CLI, validated through GitHub Actions, and displayed on existing GitHub Pages site. Self-service submission with anti-gaming measures.

**Key Features**:
- `agentready submit` CLI command (creates PR automatically)
- GitHub Action validation (re-runs assessment, verifies ownership)
- Jekyll-based leaderboard integrated into existing `docs/` site
- Multiple views: overall, by-language, by-size, most-improved
- Anti-gaming: ownership verification, re-assessment, rate limiting

---

## Architecture Overview

```
┌─────────────────┐
│  User runs:     │
│  agentready     │──┐
│  submit         │  │
└─────────────────┘  │
                     │
                     ▼
         ┌───────────────────────┐
         │  PyGithub creates PR  │
         │  to agentready/       │
         │  agentready repo      │
         └───────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  GitHub Action:       │
         │  - Validates schema   │
         │  - Checks ownership   │
         │  - Re-runs assessment │
         │  - Compares scores    │
         └───────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Maintainer merges PR │
         └───────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  GitHub Action:       │
         │  - Runs aggregation   │
         │  - Generates JSON     │
         │  - Rebuilds Jekyll    │
         └───────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Leaderboard updated  │
         │  at agentready.dev/   │
         │  leaderboard/         │
         └───────────────────────┘
```

---

## Component 1: CLI Submit Command

**File**: `src/agentready/cli/submit.py`

**Responsibilities**:
1. Validate `GITHUB_TOKEN` environment variable
2. Find assessment file (latest or specified with `-f`)
3. Extract repository metadata (org, repo, score)
4. Verify submitter has commit access to repo (PyGithub)
5. Fork `agentready/agentready` (if not already forked)
6. Create branch: `leaderboard-{org}-{repo}-{timestamp}`
7. Commit assessment to `submissions/{org}/{repo}/{timestamp}-assessment.json`
8. Create PR with template body
9. Return PR URL to user

**CLI Signature**:
```python
@cli.command()
@click.argument("repository", type=click.Path(exists=True), required=False, default=".")
@click.option("-f", "--file", "assessment_file", type=click.Path(exists=True),
              help="Path to assessment JSON file (default: latest in .agentready/)")
@click.option("--dry-run", is_flag=True, help="Show what would be submitted without creating PR")
def submit(repository, assessment_file, dry_run):
    """Submit assessment results to AgentReady leaderboard."""
```

**Key Implementation Details**:

```python
# Filename format (ISO 8601, filesystem-safe)
timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
filename = f"{timestamp}-assessment.json"
submission_path = f"submissions/{org}/{repo}/{filename}"

# Example: submissions/anthropics/claude-code/2025-12-03T14-30-45-assessment.json

# Ownership verification
gh = Github(token)
submitted_repo = gh.get_repo(f"{org}/{repo}")
user = gh.get_user()

# Check if user is collaborator OR owner
is_collaborator = submitted_repo.has_in_collaborators(user.login)
is_owner = submitted_repo.owner.login == user.login

if not (is_collaborator or is_owner):
    raise PermissionError(f"You must have commit access to {org}/{repo}")

# PR body template
pr_body = f"""## Leaderboard Submission

**Repository**: [{org}/{repo}](https://github.com/{org}/{repo})
**Score**: {score:.1f}/100
**Submitted by**: @{user.login}

### Validation Checklist

- [ ] Repository exists and is public
- [ ] Submitter has commit access
- [ ] Assessment re-run passes (±2 points tolerance)
- [ ] JSON schema valid

*Automated validation will run on this PR.*
"""
```

**Dependencies**:
- `PyGithub` (add to `pyproject.toml`)
- Existing `Assessment` model for JSON validation

**Error Handling**:
- Missing `GITHUB_TOKEN` → user-friendly error with setup instructions
- No assessment file found → suggest `agentready assess` first
- Non-GitHub repo → error (only GitHub supported)
- Permission denied → explain commit access requirement
- API rate limit → retry with exponential backoff

**Testing Strategy**:
- Unit tests: Mock `Github` API calls
- Integration tests: Use test GitHub org/repo
- Dry-run mode for manual verification

---

## Component 2: Validation GitHub Action

**File**: `.github/workflows/validate-leaderboard-submission.yml`

**Trigger**: PR with changes to `submissions/**/*-assessment.json`

**Jobs**:

### Job 1: `validate`

**Steps**:

1. **Checkout PR branch** (`actions/checkout@v4`)
   - Use `github.event.pull_request.head.sha`

2. **Set up Python 3.12** (`actions/setup-python@v5`)

3. **Install AgentReady**
   ```bash
   pip install uv
   uv venv
   source .venv/bin/activate
   uv pip install -e .
   ```

4. **Extract submission details**
   ```bash
   CHANGED_FILE=$(git diff --name-only origin/main...HEAD | grep 'submissions/.*-assessment.json' | head -1)
   REPO_URL=$(jq -r '.repository.url' "$CHANGED_FILE")
   CLAIMED_SCORE=$(jq -r '.overall_score' "$CHANGED_FILE")
   ```

5. **Verify repository exists and is public**
   ```bash
   ORG_REPO=$(echo "$REPO_URL" | sed 's|https://github.com/||')
   gh repo view "$ORG_REPO" --json isPrivate -q '.isPrivate' | grep -q false
   ```

6. **Verify submitter has access**
   ```bash
   SUBMITTER="${{ github.event.pull_request.user.login }}"
   # Check collaborator status OR ownership
   gh api "/repos/$ORG_REPO/collaborators/$SUBMITTER" || \
   gh api "/repos/$ORG_REPO" -q '.owner.login' | grep -q "$SUBMITTER"
   ```

7. **Validate JSON schema**
   ```bash
   agentready validate-report "$CHANGED_FILE"
   ```

8. **Re-run assessment**
   ```bash
   git clone "$REPO_URL" /tmp/repo-to-assess
   agentready assess /tmp/repo-to-assess --output-dir /tmp/validation
   ACTUAL_SCORE=$(jq -r '.overall_score' /tmp/validation/assessment-latest.json)
   ```

9. **Compare scores** (±2 point tolerance)
   ```bash
   DIFF=$(echo "$ACTUAL - $CLAIMED" | bc -l | sed 's/-//')
   if (( $(echo "$DIFF > 2" | bc -l) )); then
     echo "::error::Score mismatch: claimed $CLAIMED, actual $ACTUAL (diff: $DIFF)"
     exit 1
   fi
   ```

10. **Comment on PR** (success or failure)
    ```javascript
    // actions/github-script@v7
    const body = `## Validation Results

✅ **PASSED** - All validation checks successful

- Claimed score: ${claimed}
- Actual score: ${actual}
- Difference: ${diff} points

Ready for merge!`;

    github.rest.issues.createComment({...});
    ```

**Security Considerations**:
- Never trust submitted JSON (always re-run assessment)
- Clone repos in sandboxed `/tmp` directory
- Use `actions/checkout` with explicit SHA (prevent TOCTOU)
- Rate limit: Max 1 submission per repo per 24 hours (check existing files)

---

## Component 3: Aggregation Script

**File**: `scripts/generate-leaderboard-data.py`

**Trigger**: GitHub Action on push to `main` (after PR merge)

**Responsibilities**:
1. Scan `submissions/` directory recursively
2. Parse all `*-assessment.json` files
3. Group by repository (multiple submissions = historical data)
4. Calculate rankings (overall, by-language, by-size)
5. Identify "most improved" (biggest score delta)
6. Generate `docs/_data/leaderboard.json`

**Output Schema**:
```json
{
  "generated_at": "2025-12-03T14:30:45Z",
  "total_repositories": 42,
  "overall": [
    {
      "rank": 1,
      "repo": "anthropics/claude-code",
      "org": "anthropics",
      "name": "claude-code",
      "score": 95.2,
      "tier": "Platinum",
      "language": "TypeScript",
      "size": "Large",
      "last_updated": "2025-12-03",
      "url": "https://github.com/anthropics/claude-code",
      "history": [
        {"date": "2025-11-15", "score": 88.1},
        {"date": "2025-12-03", "score": 95.2}
      ]
    }
  ],
  "by_language": {
    "Python": [...],
    "TypeScript": [...],
    "Go": [...],
    "Rust": [...]
  },
  "by_size": {
    "Small": [...],
    "Medium": [...],
    "Large": [...],
    "Enterprise": [...]
  },
  "most_improved": [
    {
      "rank": 1,
      "repo": "example/repo",
      "improvement": 12.5,
      "from_score": 72.0,
      "to_score": 84.5,
      "from_date": "2025-11-12",
      "to_date": "2025-12-03",
      "days": 21
    }
  ]
}
```

**Size Categories** (based on `repository.size_category` in assessment):
- **Small**: < 1,000 LOC
- **Medium**: 1,000 - 10,000 LOC
- **Large**: 10,000 - 100,000 LOC
- **Enterprise**: > 100,000 LOC

**Implementation Outline**:
```python
def scan_submissions(submissions_dir: Path) -> dict[str, list[Assessment]]:
    """Scan submissions/ directory and group by repository."""
    repos = defaultdict(list)

    for json_file in submissions_dir.rglob("*-assessment.json"):
        # Path format: submissions/{org}/{repo}/{timestamp}-assessment.json
        parts = json_file.parts
        org = parts[-3]
        repo = parts[-2]

        with open(json_file) as f:
            assessment = json.load(f)

        repos[f"{org}/{repo}"].append({
            "assessment": assessment,
            "timestamp": json_file.stem.replace("-assessment", "")
        })

    return repos

def generate_leaderboard_data(repos: dict) -> dict:
    """Generate leaderboard.json structure."""
    overall = []
    by_language = defaultdict(list)
    by_size = defaultdict(list)
    most_improved = []

    for repo_name, submissions in repos.items():
        # Sort by timestamp (most recent first)
        submissions.sort(key=lambda x: x["timestamp"], reverse=True)
        latest = submissions[0]["assessment"]

        entry = {
            "repo": repo_name,
            "org": repo_name.split("/")[0],
            "name": repo_name.split("/")[1],
            "score": latest["overall_score"],
            "tier": latest["certification_level"],
            "language": latest["repository"]["primary_language"],
            "size": latest["repository"]["size_category"],
            "last_updated": submissions[0]["timestamp"][:10],  # YYYY-MM-DD
            "url": latest["repository"]["url"],
            "history": [
                {"date": s["timestamp"][:10], "score": s["assessment"]["overall_score"]}
                for s in submissions
            ]
        }

        overall.append(entry)
        by_language[entry["language"]].append(entry)
        by_size[entry["size"]].append(entry)

        # Calculate improvement
        if len(submissions) > 1:
            oldest = submissions[-1]["assessment"]
            improvement = latest["overall_score"] - oldest["overall_score"]

            if improvement > 0:
                most_improved.append({
                    "repo": repo_name,
                    "improvement": improvement,
                    "from_score": oldest["overall_score"],
                    "to_score": latest["overall_score"],
                    "from_date": submissions[-1]["timestamp"][:10],
                    "to_date": submissions[0]["timestamp"][:10],
                    "days": (
                        datetime.fromisoformat(submissions[0]["timestamp"][:19]) -
                        datetime.fromisoformat(submissions[-1]["timestamp"][:19])
                    ).days
                })

    # Sort rankings
    overall.sort(key=lambda x: x["score"], reverse=True)
    for lang in by_language:
        by_language[lang].sort(key=lambda x: x["score"], reverse=True)
    for size in by_size:
        by_size[size].sort(key=lambda x: x["score"], reverse=True)
    most_improved.sort(key=lambda x: x["improvement"], reverse=True)

    # Add ranks
    for i, entry in enumerate(overall, 1):
        entry["rank"] = i

    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_repositories": len(overall),
        "overall": overall,
        "by_language": dict(by_language),
        "by_size": dict(by_size),
        "most_improved": most_improved[:20]  # Top 20
    }
```

**GitHub Action** (`.github/workflows/update-leaderboard.yml`):
```yaml
name: Update Leaderboard

on:
  push:
    branches: [main]
    paths:
      - 'submissions/**/*-assessment.json'

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Generate leaderboard data
        run: |
          pip install uv
          uv venv
          source .venv/bin/activate
          uv pip install -e .
          python scripts/generate-leaderboard-data.py

      - name: Commit updated data
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/_data/leaderboard.json
          git commit -m "chore: update leaderboard data [skip ci]" || true
          git push
```

---

## Component 4: Jekyll Leaderboard Pages

**Files**:
- `docs/leaderboard/index.md` - Main leaderboard
- `docs/leaderboard/by-language.md` - Language-specific rankings
- `docs/leaderboard/most-improved.md` - Improvement tracking
- `docs/assets/css/leaderboard.css` - Styling

### Main Leaderboard Page

**File**: `docs/leaderboard/index.md`

```markdown
---
layout: default
title: AgentReady Leaderboard
description: Community-submitted repository assessments ranked by agent-readiness
---

# 🏆 AgentReady Leaderboard

Community-driven rankings of agent-ready repositories.

{% assign sorted = site.data.leaderboard.overall %}

## 🥇 Top 10 Repositories

<div class="leaderboard-top10">
{% for entry in sorted limit:10 %}
  <div class="leaderboard-card tier-{{ entry.tier | downcase }}">
    <div class="rank">#{{ forloop.index }}</div>
    <div class="repo-info">
      <h3><a href="{{ entry.url }}">{{ entry.repo }}</a></h3>
      <div class="meta">
        <span class="language">{{ entry.language }}</span>
        <span class="size">{{ entry.size }}</span>
      </div>
    </div>
    <div class="score-badge">
      <span class="score">{{ entry.score | round: 1 }}</span>
      <span class="tier">{{ entry.tier }}</span>
    </div>
  </div>
{% endfor %}
</div>

## 📊 All Repositories

<table class="leaderboard-table">
  <thead>
    <tr>
      <th>Rank</th>
      <th>Repository</th>
      <th>Score</th>
      <th>Tier</th>
      <th>Language</th>
      <th>Size</th>
      <th>Last Updated</th>
    </tr>
  </thead>
  <tbody>
    {% for entry in sorted %}
    <tr class="tier-{{ entry.tier | downcase }}">
      <td class="rank">{{ entry.rank }}</td>
      <td class="repo-name">
        <a href="{{ entry.url }}">{{ entry.repo }}</a>
      </td>
      <td class="score">{{ entry.score | round: 1 }}</td>
      <td>
        <span class="badge {{ entry.tier | downcase }}">{{ entry.tier }}</span>
      </td>
      <td>{{ entry.language }}</td>
      <td>{{ entry.size }}</td>
      <td>{{ entry.last_updated }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>

## 📈 Submit Your Repository

```bash
# 1. Run assessment
agentready assess .

# 2. Submit to leaderboard (requires GITHUB_TOKEN)
agentready submit

# 3. Wait for validation and PR merge
```

**Requirements**:
- GitHub repository (public)
- Commit access to repository
- `GITHUB_TOKEN` environment variable

[Learn more about submission →](../user-guide.html#leaderboard)

---

*Leaderboard updated: {{ site.data.leaderboard.generated_at }}*
*Total repositories: {{ site.data.leaderboard.total_repositories }}*
```

### By-Language Page

**File**: `docs/leaderboard/by-language.md`

```markdown
---
layout: default
title: Leaderboard by Language
---

# 📚 Leaderboard by Language

{% for lang_data in site.data.leaderboard.by_language %}
{% assign language = lang_data[0] %}
{% assign repos = lang_data[1] %}

## {{ language }}

<table class="leaderboard-table">
  <thead>
    <tr>
      <th>Rank</th>
      <th>Repository</th>
      <th>Score</th>
      <th>Tier</th>
    </tr>
  </thead>
  <tbody>
    {% for entry in repos %}
    <tr>
      <td>{{ forloop.index }}</td>
      <td><a href="{{ entry.url }}">{{ entry.repo }}</a></td>
      <td>{{ entry.score | round: 1 }}</td>
      <td><span class="badge {{ entry.tier | downcase }}">{{ entry.tier }}</span></td>
    </tr>
    {% endfor %}
  </tbody>
</table>

{% endfor %}
```

### Most Improved Page

**File**: `docs/leaderboard/most-improved.md`

```markdown
---
layout: default
title: Most Improved Repositories
---

# 📈 Most Improved Repositories

Repositories with the biggest score improvements over time.

<table class="leaderboard-table">
  <thead>
    <tr>
      <th>Rank</th>
      <th>Repository</th>
      <th>Improvement</th>
      <th>From</th>
      <th>To</th>
      <th>Timeframe</th>
    </tr>
  </thead>
  <tbody>
    {% for entry in site.data.leaderboard.most_improved %}
    <tr>
      <td>{{ forloop.index }}</td>
      <td><a href="https://github.com/{{ entry.repo }}">{{ entry.repo }}</a></td>
      <td class="improvement">+{{ entry.improvement | round: 1 }}</td>
      <td>{{ entry.from_score | round: 1 }}</td>
      <td>{{ entry.to_score | round: 1 }}</td>
      <td>{{ entry.days }} days</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
```

### CSS Styling

**File**: `docs/assets/css/leaderboard.css`

```css
/* Leaderboard Top 10 Cards */
.leaderboard-top10 {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}

.leaderboard-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid #e1e4e8;
  border-radius: 8px;
  background: white;
  transition: transform 0.2s, box-shadow 0.2s;
}

.leaderboard-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Tier-based borders */
.leaderboard-card.tier-platinum { border-color: #b8b5ff; }
.leaderboard-card.tier-gold { border-color: #ffd700; }
.leaderboard-card.tier-silver { border-color: #c0c0c0; }
.leaderboard-card.tier-bronze { border-color: #cd7f32; }

.leaderboard-card .rank {
  font-size: 2rem;
  font-weight: bold;
  color: #586069;
  min-width: 50px;
  text-align: center;
}

.leaderboard-card .repo-info {
  flex: 1;
}

.leaderboard-card .repo-info h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}

.leaderboard-card .repo-info h3 a {
  color: #0366d6;
  text-decoration: none;
}

.leaderboard-card .meta {
  display: flex;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #586069;
}

.leaderboard-card .score-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem 1rem;
  background: #f6f8fa;
  border-radius: 6px;
}

.leaderboard-card .score {
  font-size: 2rem;
  font-weight: bold;
  line-height: 1;
}

.leaderboard-card .tier {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #586069;
  margin-top: 0.25rem;
}

/* Tier colors for scores */
.tier-platinum .score { color: #7c3aed; }
.tier-gold .score { color: #ca8a04; }
.tier-silver .score { color: #71717a; }
.tier-bronze .score { color: #c2410c; }

/* Leaderboard Table */
.leaderboard-table {
  width: 100%;
  border-collapse: collapse;
  margin: 2rem 0;
  font-size: 0.9rem;
}

.leaderboard-table thead {
  background: #f6f8fa;
  border-bottom: 2px solid #e1e4e8;
}

.leaderboard-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  color: #24292e;
}

.leaderboard-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e1e4e8;
}

.leaderboard-table tr:hover {
  background: #f6f8fa;
}

.leaderboard-table .rank {
  font-weight: bold;
  color: #586069;
  text-align: center;
  width: 60px;
}

.leaderboard-table .score {
  font-weight: bold;
  font-size: 1.1rem;
  text-align: center;
  width: 80px;
}

.leaderboard-table .repo-name a {
  color: #0366d6;
  text-decoration: none;
  font-family: 'SF Mono', Monaco, 'Courier New', monospace;
}

.leaderboard-table .repo-name a:hover {
  text-decoration: underline;
}

/* Tier badges */
.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge.platinum { background: #ede9fe; color: #7c3aed; }
.badge.gold { background: #fef3c7; color: #ca8a04; }
.badge.silver { background: #f4f4f5; color: #71717a; }
.badge.bronze { background: #fed7aa; color: #c2410c; }

/* Improvement column */
.improvement {
  color: #22c55e;
  font-weight: bold;
  font-size: 1.1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .leaderboard-top10 {
    grid-template-columns: 1fr;
  }

  .leaderboard-table {
    font-size: 0.8rem;
  }

  .leaderboard-table th,
  .leaderboard-table td {
    padding: 0.5rem;
  }
}
```

---

## Integration with Existing Docs

### Update Navigation

**File**: `docs/_layouts/default.html` (or `_config.yml`)

Add leaderboard to navigation:

```yaml
# _config.yml
navigation:
  - title: Home
    url: /
  - title: User Guide
    url: /user-guide.html
  - title: Developer Guide
    url: /developer-guide.html
  - title: Attributes
    url: /attributes.html
  - title: Leaderboard  # NEW
    url: /leaderboard/
  - title: API Reference
    url: /api-reference.html
```

### Update User Guide

**File**: `docs/user-guide.md`

Add section on leaderboard submission:

```markdown
## Leaderboard Submission

Submit your repository's assessment to the public AgentReady leaderboard.

### Prerequisites

1. GitHub personal access token with `public_repo` scope
2. Commit access to the repository you're submitting
3. Completed assessment (run `agentready assess` first)

### Steps

```bash
# 1. Set GitHub token
export GITHUB_TOKEN=ghp_your_token_here

# 2. Run assessment
agentready assess .

# 3. Submit to leaderboard
agentready submit

# 4. Wait for PR to be created
# 5. Validation runs automatically
# 6. Maintainer reviews and merges
# 7. Leaderboard updates within minutes
```

### Validation Process

Your submission will be automatically validated:

- ✅ Repository exists and is public
- ✅ You have commit access to the repository
- ✅ Assessment JSON schema is valid
- ✅ Score re-verification (±2 points tolerance)

If validation fails, the PR will have a comment explaining the issue.

### Rate Limits

- Maximum 1 submission per repository per 24 hours
- Re-submissions allowed to track improvement over time
```

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_submit.py`

```python
import pytest
from unittest.mock import Mock, patch
from agentready.cli.submit import submit

def test_submit_missing_token(cli_runner):
    """Test that missing GITHUB_TOKEN raises error."""
    with patch.dict('os.environ', {}, clear=True):
        result = cli_runner.invoke(submit)
        assert result.exit_code == 1
        assert "GITHUB_TOKEN" in result.output

def test_submit_no_assessment(cli_runner, tmp_path):
    """Test that missing assessment file raises error."""
    with patch.dict('os.environ', {'GITHUB_TOKEN': 'fake-token'}):
        result = cli_runner.invoke(submit, [str(tmp_path)])
        assert result.exit_code == 1
        assert "No assessment found" in result.output

@patch('agentready.cli.submit.Github')
def test_submit_dry_run(mock_github, cli_runner, tmp_path, sample_assessment):
    """Test dry-run mode doesn't create PR."""
    assessment_file = tmp_path / ".agentready" / "assessment-latest.json"
    assessment_file.parent.mkdir(parents=True)
    assessment_file.write_text(sample_assessment)

    with patch.dict('os.environ', {'GITHUB_TOKEN': 'fake-token'}):
        result = cli_runner.invoke(submit, [str(tmp_path), '--dry-run'])
        assert result.exit_code == 0
        assert "Would submit to:" in result.output
        mock_github.assert_not_called()
```

### Integration Tests

**File**: `tests/integration/test_leaderboard_workflow.py`

```python
import pytest
from pathlib import Path
from scripts.generate_leaderboard_data import scan_submissions, generate_leaderboard_data

def test_aggregation_script(tmp_path):
    """Test leaderboard data generation from submissions."""
    # Create mock submissions
    submissions_dir = tmp_path / "submissions"
    (submissions_dir / "org1" / "repo1").mkdir(parents=True)
    (submissions_dir / "org2" / "repo2").mkdir(parents=True)

    # Write sample assessments
    # ... (create JSON files)

    # Run aggregation
    repos = scan_submissions(submissions_dir)
    data = generate_leaderboard_data(repos)

    assert data["total_repositories"] == 2
    assert len(data["overall"]) == 2
    assert data["overall"][0]["rank"] == 1
```

---

## Acceptance Criteria

### CLI Submit Command
- [ ] `agentready submit` creates PR successfully
- [ ] `agentready submit -f <file>` uses specified assessment
- [ ] `--dry-run` flag shows preview without creating PR
- [ ] Error handling for missing token, file, permissions
- [ ] Filename format: `YYYY-MM-DDTHH-MM-SS-assessment.json`

### Validation Workflow
- [ ] Validates JSON schema
- [ ] Verifies repository exists and is public
- [ ] Checks submitter has commit access
- [ ] Re-runs assessment and compares scores (±2 tolerance)
- [ ] Comments on PR with validation results
- [ ] Blocks merge if validation fails

### Aggregation Script
- [ ] Scans `submissions/` recursively
- [ ] Generates `docs/_data/leaderboard.json`
- [ ] Calculates overall, by-language, by-size, most-improved rankings
- [ ] Handles multiple submissions per repo (history tracking)
- [ ] Runs automatically on PR merge

### Leaderboard Pages
- [ ] Main leaderboard displays top 10 cards + full table
- [ ] By-language page shows per-language rankings
- [ ] Most-improved page shows biggest score deltas
- [ ] Responsive design (mobile-friendly)
- [ ] Tier-based color coding (Platinum/Gold/Silver/Bronze)
- [ ] Links to GitHub repositories

---

## Implementation Order

1. **CLI Submit Command** (foundation)
   - Implement `src/agentready/cli/submit.py`
   - Add PyGithub dependency
   - Write unit tests
   - Manual testing with dry-run

2. **Validation Workflow** (anti-gaming)
   - Create `.github/workflows/validate-leaderboard-submission.yml`
   - Test with sample PR
   - Refine error messages

3. **Aggregation Script** (data pipeline)
   - Implement `scripts/generate-leaderboard-data.py`
   - Create `.github/workflows/update-leaderboard.yml`
   - Test with sample submissions

4. **Leaderboard Pages** (UI)
   - Create `docs/leaderboard/` directory
   - Implement Jekyll templates
   - Add CSS styling
   - Update navigation

---

## Dependencies

### Python Packages
```toml
# pyproject.toml
[project.dependencies]
PyGithub = "^2.1.1"  # NEW
```

### GitHub Actions
- `actions/checkout@v4`
- `actions/setup-python@v5`
- `actions/github-script@v7`

### External Tools
- `jq` (JSON parsing in bash)
- `bc` (score comparison in bash)
- `gh` CLI (GitHub API access)

---

## Example Usage Flow

```bash
# Developer workflow
cd ~/my-awesome-project

# 1. Run assessment
agentready assess .
# => .agentready/assessment-20251203-143045.json

# 2. Preview submission
agentready submit --dry-run
# => Would submit to: submissions/myorg/my-awesome-project/2025-12-03T14-30-45-assessment.json
# => Repository: myorg/my-awesome-project
# => Score: 82.5/100

# 3. Submit to leaderboard
export GITHUB_TOKEN=ghp_xxxxx
agentready submit
# => Created fork: myusername/agentready
# => ✅ Submission successful!
# => PR: https://github.com/agentready/agentready/pull/123

# 4. Wait for validation (automated)
# => GitHub Action runs on PR
# => Comments: "✅ PASSED - All validation checks successful"

# 5. Maintainer merges PR
# => Aggregation script runs
# => Leaderboard updates

# 6. View results
open https://agentready.dev/leaderboard/
# => See your repo on the leaderboard!
```

---

## Future Enhancements (Out of Scope)

- **Badges**: Generate `[![AgentReady Score](https://img.shields.io/badge/...)](...)` for README
- **API Endpoint**: `/api/leaderboard.json` for programmatic access
- **Webhooks**: Auto-submit on new releases
- **Private Leaderboards**: Organization-specific leaderboards
- **Historical Charts**: Score trends over time (Chart.js)
- **Filters/Search**: Client-side filtering by language, tier, org
- **Notification**: Email/Slack when submission is merged

---

## Open Questions / Decisions Needed

1. **Should we auto-submit AgentReady itself?** (dogfooding)
2. **Rate limiting**: 1 submission per repo per 24 hours sufficient?
3. **Minimum score**: Allow all scores or require >40 (Bronze)?
4. **Historical limit**: Keep all submissions or cap at last 10 per repo?
5. **Moderation**: Allow manual removal of spam submissions?

---

## References

- **Existing CLI**: `src/agentready/cli/main.py` (patterns for Click commands)
- **Assessment Model**: `src/agentready/models/assessment.py` (JSON schema)
- **GitHub Pages**: `docs/` (Jekyll site structure)
- **PyGithub Docs**: https://pygithub.readthedocs.io/
- **GitHub Actions**: https://docs.github.com/en/actions

---

**Ready for Implementation**: This cold-start prompt provides complete context for an AI agent or developer to implement the leaderboard feature end-to-end without additional conversation history.
