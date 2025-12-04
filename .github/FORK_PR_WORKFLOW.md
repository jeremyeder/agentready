# Fork PR Workflow Documentation

## Overview

AgentReady uses a two-workflow pattern to handle pull requests from forked repositories while maintaining security and functionality.

## Problem

GitHub Actions restricts permissions for pull requests from forks to prevent malicious code from:
- Writing to the repository
- Posting comments
- Modifying issues
- Accessing secrets

This security measure means fork PRs run with read-only permissions, even if the workflow declares `pull-requests: write`.

## Solution

We split the workflow into two separate workflows:

### 1. Assessment Workflow (`agentready-assessment.yml`)

**Runs on**: Fork PR (read-only permissions)

**Responsibilities**:
- Checkout code from the PR
- Install AgentReady
- Run assessment
- Upload artifacts (reports + PR metadata)

**Key Points**:
- Only requires `contents: read` permission
- Saves PR number to artifact for later use
- Uses `if-no-files-found: warn` to avoid failure if `.agentready/` missing

### 2. Comment Workflow (`agentready-comment.yml`)

**Runs on**: Base repository (write permissions)

**Trigger**: When assessment workflow completes successfully

**Responsibilities**:
- Download assessment artifacts
- Download PR metadata (PR number)
- Post comment to PR with assessment results

**Key Points**:
- Has `pull-requests: write` permission (runs in base repo context)
- Uses `workflow_run` trigger to run in trusted context
- Only runs if assessment succeeded

## Workflow Diagram

```
Fork PR Created
  ↓
[Assessment Workflow] (read-only)
  ├─ Run assessment
  ├─ Upload report artifacts
  └─ Upload PR number
  ↓
[Comment Workflow] (write permissions)
  ├─ Download artifacts
  └─ Post comment to PR
```

## Testing

To test these workflows:

1. **Create a test fork PR**:
   ```bash
   # From a fork
   git checkout -b test-assessment
   # Make some changes
   git push origin test-assessment
   # Create PR
   ```

2. **Verify assessment runs**:
   - Check Actions tab for "AgentReady Assessment" workflow
   - Verify it completes successfully
   - Check that artifacts are uploaded

3. **Verify comment posts**:
   - Check Actions tab for "AgentReady PR Comment" workflow
   - Verify it triggers after assessment completes
   - Check PR for assessment comment

## Common Issues

### Assessment report not found

**Symptom**: "No files were found with the provided path: .agentready/"

**Cause**: AgentReady didn't create `.agentready/` directory

**Fix**: Workflow now uses `if-no-files-found: warn` instead of failing

### Comment workflow doesn't trigger

**Symptom**: Comment workflow never runs

**Possible causes**:
1. Assessment workflow failed (comment only runs on success)
2. Workflow name mismatch in `workflow_run.workflows` filter
3. Event type isn't `pull_request`

**Fix**: Check workflow names match exactly and assessment succeeded

### PR number not found

**Symptom**: "No PR number found" in comment workflow logs

**Cause**: PR metadata artifact wasn't uploaded or downloaded

**Fix**: Verify both workflows upload/download `pr-metadata` artifact correctly

## Security Considerations

### Safe Patterns

✅ **Reading from artifacts**: Safe - artifacts are immutable once created
✅ **PR number from artifact**: Safe - integer value, no injection risk
✅ **Using environment variables**: Safe - proper escaping with `env:`

### Unsafe Patterns to Avoid

❌ **Direct use of PR title/body in `run:`**: Command injection risk
❌ **Running untrusted code from fork**: Security risk
❌ **Exposing secrets to fork PRs**: Credential leak risk

## References

- [GitHub: Keeping workflows secure](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [GitHub: Using workflow_run](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_run)
- [GitHub: Command injection prevention](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions#understanding-the-risk-of-script-injections)

## Maintainer Notes

When modifying these workflows:

1. **Never merge the workflows back together** - the split is intentional for security
2. **Always use `env:` for GitHub context variables** - prevents injection
3. **Keep fork workflow read-only** - never add write permissions to assessment workflow
4. **Test with actual fork PRs** - permissions behave differently than same-repo PRs
5. **Validate YAML before committing** - syntax errors break CI for everyone

---

**Last Updated**: 2025-12-04
**Related Issues**: #162 (fork PR permission failures)
**Related Workflows**:
- `.github/workflows/agentready-assessment.yml`
- `.github/workflows/agentready-comment.yml`
