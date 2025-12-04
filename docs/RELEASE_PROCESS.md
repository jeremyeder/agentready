# Release Process

## Overview

AgentReady uses automated semantic releases based on conventional commits. Releases are created automatically when commits are merged to the `main` branch.

## Release Types

Releases follow [Semantic Versioning](https://semver.org/):

- **Major (X.0.0)**: Breaking changes (commit prefix: `feat!:` or `fix!:` or `BREAKING CHANGE:`)
- **Minor (x.Y.0)**: New features (commit prefix: `feat:`)
- **Patch (x.y.Z)**: Bug fixes (commit prefix: `fix:`)

## Automated Release Workflow

When commits are merged to `main`:

1. **Semantic-release analyzes** commit messages since the last release
2. **Version is determined** based on conventional commit types
3. **CHANGELOG.md is updated** with release notes
4. **pyproject.toml version** is bumped automatically
5. **Git tag is created** (e.g., `v1.0.0`)
6. **GitHub Release is published** with release notes
7. **Changes are committed** back to main with `[skip ci]`
8. **PyPI packages published** to Test PyPI and production PyPI (OIDC authentication)
9. **Post-release housekeeping** executes:
   - Release summary generation with installation links
   - Self-assessment runs and commits updated scores
   - Multi-platform Docker images built and pushed to ghcr.io
   - Documentation deployed to GitHub Pages
   - Version synchronized across all documentation files

### 📊 Complete Pipeline Visualization

For a detailed, interactive visualization of the entire release process with flowcharts and sequence diagrams, see:

**[Release Process Visualization →](release-process-visualization.html)**

The visualization includes:
- High-level release flow with decision points
- Semantic release plugin execution order
- Version synchronization across files
- PyPI publishing with OIDC trusted publishing
- All 5 post-release housekeeping steps
- Docker multi-platform build process
- Documentation deployment flow
- Typical release timeline (0:00 - 3:30)

## Real-World Example: v2.12.1 Release

Here's an actual release that demonstrates the complete automated pipeline in action:

### Timeline

| Time | Step | Details |
|------|------|---------|
| 0:00 | **Commit Merged** | PR #155 merged: `fix: disable attestations for Test PyPI` |
| 0:05 | **Semantic Analysis** | Detected `fix:` commit → patch release (2.12.0 → 2.12.1) |
| 0:15 | **Version Bump** | Updated pyproject.toml, CLAUDE.md, README.md |
| 0:30 | **CHANGELOG Generated** | Release notes extracted from commit messages |
| 0:45 | **GitHub Release Created** | Tag v2.12.1 created with assets |
| 1:00 | **Test PyPI Published** | Package uploaded to test.pypi.org (attestations: false) |
| 1:15 | **Production PyPI Published** | Package uploaded to pypi.org (attestations: true) |
| 1:30 | **Release Summary Generated** | GitHub Actions summary with installation commands |
| 1:45 | **Self-Assessment Run** | AgentReady assessed itself: 80.0/100 (Gold) |
| 2:00 | **Self-Assessment Committed** | Results pushed to examples/self-assessment/ |
| 2:15 | **Docker Images Built** | Multi-platform build (linux/amd64, linux/arm64) |
| 2:30 | **Docker Images Pushed** | Published to ghcr.io/ambient-code/agentready:2.12.1 and :latest |
| 2:45 | **Documentation Deployed** | docs/ pushed to GitHub Pages |
| 3:00 | **✅ Release Complete** | All artifacts published, quality validated |

### What Was Published

**PyPI Package**:
- Production: https://pypi.org/project/agentready/2.12.1/
- Test: https://test.pypi.org/project/agentready/2.12.1/
- Installation: `pip install agentready==2.12.1`

**Docker Images**:
- `ghcr.io/ambient-code/agentready:2.12.1` (immutable)
- `ghcr.io/ambient-code/agentready:latest` (rolling)
- Usage: `docker run ghcr.io/ambient-code/agentready:2.12.1 assess /path/to/repo`

**Documentation**:
- GitHub Pages: https://ambient-code.github.io/agentready/
- Updated with v2.12.1 references

**GitHub Release**:
- Release Notes: https://github.com/ambient-code/agentready/releases/tag/v2.12.1
- Source code archives + distribution files

### Commit That Triggered It

```bash
fix: disable attestations for Test PyPI to avoid conflict (#155)

- Disable attestations for Test PyPI publish step
- Keep attestations enabled for production PyPI
- Prevents "attestation files already exist" error when publishing to both

The pypa/gh-action-pypi-publish action creates attestation files (.publish.attestation)
during the first publish. When we try to publish to a second repository in the same
workflow run, it tries to create them again, causing a conflict.

Solution: Disable attestations for Test PyPI (validation only), enable for production.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude <noreply@anthropic.com>
```

### Why This Release Was Successful

1. **Proper conventional commit** (`fix:`) triggered semantic-release
2. **No PR reference conflicts** (all PRs existed in the repository)
3. **OIDC authentication** worked without tokens
4. **Attestation settings** correctly configured (false for Test PyPI, true for production)
5. **All housekeeping steps** completed without errors
6. **Self-assessment** validated repository quality (80.0/100)
7. **Multi-platform Docker builds** succeeded with cache

This is the gold standard for releases in this repository.

## Conventional Commit Format

All commits must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Common Types

- `feat:` - New feature (triggers minor release)
- `fix:` - Bug fix (triggers patch release)
- `docs:` - Documentation changes (no release)
- `chore:` - Maintenance tasks (no release)
- `refactor:` - Code refactoring (no release)
- `test:` - Test changes (no release)
- `ci:` - CI/CD changes (no release)

### Breaking Changes

To trigger a major version bump, use one of these:

```bash
# With ! after type
feat!: redesign assessment API

# With BREAKING CHANGE footer
feat: update scoring algorithm

BREAKING CHANGE: Assessment.score is now a float instead of int
```

## Manual Release Trigger

To manually trigger a release without a commit:

```bash
# Trigger release workflow via GitHub CLI
gh workflow run release.yml

# Or via GitHub UI
# Actions → Release → Run workflow → Run workflow
```

## Pre-release Process

For alpha/beta releases (not yet configured):

```bash
# Future: Create pre-release from beta branch
git checkout -b beta
git push origin beta
```

Then update `.releaserc.json` to include beta branch configuration.

## Hotfix Process

For urgent production fixes:

1. **Create hotfix branch** from the latest release tag:

   ```bash
   git checkout -b hotfix/critical-bug v1.2.3
   ```

2. **Apply fix** with conventional commit:

   ```bash
   git commit -m "fix: resolve critical security issue"
   ```

3. **Push and create PR** to main:

   ```bash
   git push origin hotfix/critical-bug
   gh pr create --base main --title "fix: critical security hotfix"
   ```

4. **Merge to main** - Release automation handles versioning

## Rollback Procedure

To rollback a release:

### 1. Delete the tag and release

```bash
# Delete tag locally
git tag -d v1.2.3

# Delete tag remotely
git push origin :refs/tags/v1.2.3

# Delete GitHub release
gh release delete v1.2.3 --yes
```

### 2. Revert the release commit

```bash
# Find the release commit
git log --oneline | grep "chore(release)"

# Revert it
git revert <release-commit-sha>
git push origin main
```

### 3. Restore previous version

Edit `pyproject.toml` to restore the previous version number and commit.

## Release Checklist

Before a major release, ensure:

- [ ] All tests passing on main branch
- [ ] Documentation is up to date
- [ ] Security vulnerabilities addressed
- [ ] Dependencies are up to date (run `uv pip list --outdated`)
- [ ] Self-assessment score is current
- [ ] Migration guide written (if breaking changes)
- [ ] Examples updated for new features

## Monitoring Releases

After a release is published:

1. **Verify GitHub Release** - Check release notes are accurate
2. **Monitor issues** - Watch for regression reports
3. **Check workflows** - Ensure no failures in release workflow
4. **Update milestones** - Close completed milestone, create next one

## Troubleshooting

### Release workflow fails

- Check commit message format matches conventional commits
- Verify `GITHUB_TOKEN` has sufficient permissions
- Review semantic-release logs in Actions tab
- Ensure no merge conflicts in CHANGELOG.md

### Version not incrementing

- Ensure commits use conventional commit format (`feat:`, `fix:`, etc.)
- Check that commits aren't marked `[skip ci]`
- Verify `.releaserc.json` branch configuration matches current branch
- Review semantic-release dry-run output

### CHANGELOG conflicts

If CHANGELOG.md has merge conflicts:

1. Resolve conflicts manually
2. Commit the resolution
3. Semantic-release will include the fix in next release

## Resources

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Release Documentation](https://semantic-release.gitbook.io/)
- [GitHub Actions: Publishing packages](https://docs.github.com/en/actions/publishing-packages)

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 2.12.1 | 2025-12-04 | Fix PyPI attestation conflicts, automated dual publishing |
| 2.12.0 | 2025-12-04 | OIDC trusted publishing, automated PyPI releases |
| 2.9.0 | 2025-11-28 | Community leaderboard, batch assessment |
| 1.0.0 | 2025-11-21 | Initial release with core assessment engine |

---

**Last Updated**: 2025-12-04
**Maintained By**: AgentReady Team
