# CI Coverage Enforcement Configuration

This document describes the changes needed to enforce 90% test coverage in CI.

## Status

✅ **Local Enforcement Configured** - pytest will now fail if coverage drops below 90%
❌ **CI Workflow Update Required** - Manual update needed (see below)

## Changes Made

### 1. pytest Configuration (`pyproject.toml`)

Updated pytest configuration to fail when coverage drops below 90%:

```toml
[tool.pytest.ini_options]
addopts = "-v --cov=agentready --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=90"

[tool.coverage.report]
fail_under = 90
```

This ensures that:
- `pytest` command will exit with non-zero code if coverage < 90%
- Both pytest and coverage.py enforce the threshold
- XML report is generated for Codecov integration

### 2. GitHub Actions Workflow (`.github/workflows/tests.yml`)

**REQUIRED MANUAL UPDATE** (automated workflow modification not permitted):

The workflow already uploads coverage to Codecov. To enforce coverage in CI:

#### Option A: Fail on Coverage Drop (Recommended)

Update line 44 in `.github/workflows/tests.yml`:

```yaml
# Current:
- name: Run pytest
  run: |
    pytest --cov=src --cov-report=xml --cov-report=term

# Change to (enforcement now in pyproject.toml):
- name: Run pytest with coverage enforcement
  run: |
    pytest
```

The `--cov-fail-under=90` flag in `pyproject.toml` will automatically fail the job if coverage drops below 90%.

#### Option B: Add Explicit Coverage Check Step

Add a new step after pytest:

```yaml
- name: Run pytest
  run: |
    pytest

- name: Check coverage threshold
  run: |
    coverage report --fail-under=90
```

#### Option C: Use Codecov Threshold (Cloud-based)

Update Codecov step to fail on coverage drop:

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  if: matrix.python-version == '3.11'
  with:
    files: ./coverage.xml
    fail_ci_if_error: true  # Change from false to true
```

Then configure threshold in Codecov dashboard or add `.codecov.yml`:

```yaml
coverage:
  status:
    project:
      default:
        target: 90%
        threshold: 0.5%
    patch:
      default:
        target: 90%
```

## Recommended Approach

**Use Option A** - simplest and most maintainable:

1. Update `.github/workflows/tests.yml` line 44 to just run `pytest`
2. Let `pyproject.toml` configuration handle coverage enforcement
3. Keep Codecov for reporting and visualization

## Testing Locally

Run tests with coverage enforcement:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (will fail if coverage < 90%)
pytest

# View detailed coverage report
pytest --cov-report=html
open htmlcov/index.html
```

## Current Coverage

With the new comprehensive tests added in this PR:
- **CLI modules**: +1427 lines of tests (learn, align, repomix)
- **Services**: +660 lines of tests (learning_service)
- **Learners**: +500+ lines of tests (llm_enricher, code_sampler)

**Expected coverage**: 85-92% (target: 90%+)

## PR Checklist

- [x] Configure pytest to fail at <90% coverage
- [x] Add comprehensive CLI tests (learn, align, repomix)
- [x] Add comprehensive service tests (learning_service)
- [x] Add comprehensive learner tests (llm_enricher, code_sampler)
- [x] Document CI workflow changes needed
- [ ] Update `.github/workflows/tests.yml` (requires manual commit)
- [ ] Verify coverage passes 90% threshold
- [ ] Add coverage badge to README.md

## Coverage Badge

Once Codecov is configured, add badge to README.md:

```markdown
[![codecov](https://codecov.io/gh/ambient-code/agentready/branch/main/graph/badge.svg)](https://codecov.io/gh/ambient-code/agentready)
```

## Notes

- **Workflow file permissions**: GitHub Actions workflow files cannot be modified programmatically for security reasons
- **Manual update required**: Repository maintainer must update `.github/workflows/tests.yml`
- **Local enforcement works**: Developers will catch coverage drops before pushing
- **Comprehensive tests added**: ~2600+ lines of new test code covering CLI, services, and learners

---

**Last Updated**: 2025-11-22
**Issue**: #42 - Increase test coverage to 90% with CI enforcement
