# Dual Claude Integration Guide

This repository uses **two different Claude integrations** that work together for different use cases.

## 🤖 Integration Overview

| Integration | Trigger | Behavior | Use Case |
|------------|---------|----------|----------|
| **Claude Code Action** | Assign issue to `claude-bot` | Automated implementation in GitHub Actions | Autonomous feature development |
| **Direct @claude** | @mention claude in comments | Interactive conversation in comment thread | Discussion, guidance, code review |

---

## 1. Automated Implementation (Claude Code Action)

### How It Works

When you **assign an issue to `claude-bot`**:
1. GitHub Actions workflow triggers
2. Claude Code CLI spins up in runner
3. Reads `CLAUDE.md` for project context
4. Implements the issue autonomously
5. Creates feature branch and commits
6. Opens PR for review

### Configuration

**Workflow**: `.github/workflows/claude-code-action.yml`
- Triggers only on `issues.assigned` events
- Checks `if: github.event.assignee.login == 'claude-bot'`
- Uses `ANTHROPIC_API_KEY` secret

**System Prompts**:
- `CLAUDE.md` (project-level) - Automatically read
- `.github/claude-bot-prompt.md` (automation-specific) - Optional, currently commented out

### Usage

```bash
# Create issue on GitHub
# Assign to @claude-bot user
# Wait for PR to be created
```

### Example Workflow

1. Create issue: "Implement dependency freshness assessor"
2. Assign to `claude-bot`
3. Wait 2-5 minutes
4. Review PR created by claude-bot
5. Merge or request changes

---

## 2. Interactive Conversation (Direct @claude)

### How It Works

When you **@mention claude in any comment**:
1. Claude responds directly in the comment thread
2. No code is written automatically
3. Interactive back-and-forth discussion
4. You control when to apply suggestions

### Setup Required

**Install the Claude GitHub App**:
1. Navigate to https://github.com/apps/claude-ai
2. Click "Install"
3. Select `ambient-code/agentready` repository
4. Grant required permissions:
   - Read access to code and issues
   - Write access to comments
5. Complete installation

**Connect Your Account**:
1. Go to https://claude.ai/settings
2. Navigate to "Integrations"
3. Connect your GitHub account
4. Authorize the app

### Usage

```markdown
@claude How should I structure the DependencyFreshnessAssessor?
```

Claude will respond with:
- Architecture suggestions
- Code examples
- Best practices
- Questions for clarification

You then choose which suggestions to implement manually (or ask claude-bot to implement via assignment).

---

## 3. When to Use Each Integration

### Use Claude Code Action (assign to claude-bot) when:
- ✅ You want autonomous implementation
- ✅ The task is well-defined
- ✅ You're okay with reviewing a PR afterward
- ✅ You want to save development time

### Use Direct @claude when:
- ✅ You need design discussion first
- ✅ You want to explore options interactively
- ✅ You need code review feedback
- ✅ You want to implement manually with guidance
- ✅ The task has ambiguity or trade-offs

### Use Both Together:
1. Create issue with @claude mention
2. Discuss approach with interactive Claude
3. Once design is settled, assign to claude-bot
4. claude-bot implements the agreed-upon design

---

## 4. Customizing Automation Behavior

### Editing CLAUDE.md

`CLAUDE.md` is the **main source of truth** for project context:
- Architecture overview
- Development workflow
- Code quality standards
- Testing requirements

**Changes to CLAUDE.md affect both integrations.**

### Editing .github/claude-bot-prompt.md

This file provides **automation-specific instructions**:
- Feature branch naming conventions
- PR creation templates
- TDD requirements
- Commit message formats

**To enable**: Uncomment the `claude_args` line in `claude-code-action.yml`

### Example Customization

```yaml
# In .github/workflows/claude-code-action.yml
claude_args: --append-system-prompt "$(cat .github/claude-bot-prompt.md)"
```

---

## 5. Troubleshooting

### Claude Code Action Not Triggering

**Check**:
- [ ] Issue is assigned to `claude-bot` user (exact spelling)
- [ ] GitHub Actions workflow is enabled in Settings > Actions
- [ ] `ANTHROPIC_API_KEY` secret is set in repository secrets
- [ ] Workflow file syntax is valid (no YAML errors)

**View Logs**:
1. Go to Actions tab
2. Find the failed/running workflow
3. Click to view logs
4. Check "Claude Code Action" step for errors

### Direct @claude Not Responding

**Check**:
- [ ] Claude GitHub App is installed on repository
- [ ] Your GitHub account is connected at claude.ai
- [ ] You used `@claude` (not `@claude-bot`)
- [ ] Comment is on an issue or PR (not commit)

**Note**: Direct @claude may take 30-60 seconds to respond initially.

### Both Integrations Triggering

**This shouldn't happen with current config**:
- Claude Code Action only triggers on assignment to `claude-bot`
- Direct @claude responds to @mentions
- These are mutually exclusive triggers

If both respond, check that:
- Workflow file has correct `if:` condition
- You're not both assigning AND mentioning

---

## 6. Security Considerations

### API Keys
- `ANTHROPIC_API_KEY` stored as GitHub secret (encrypted)
- Never exposed in logs or PR comments
- Automatically rotated every 90 days

### Permissions
- Claude Code Action has `write` access (needed for PRs)
- Direct @claude has `read` + `comment` access only
- Both run in isolated environments

### Code Review
- **Always review PRs** created by claude-bot before merging
- Check for security issues (hardcoded secrets, injection vulnerabilities)
- Verify tests pass and coverage maintained
- Run local linters before merge

---

## 7. Cost Management

### Claude Code Action
- Uses Anthropic API (metered by tokens)
- Typical cost: $0.10-$0.50 per issue implementation
- Monitor usage in Anthropic Console

### Direct @claude
- Free for individual use
- Subject to rate limits (TBD by Anthropic)

### Best Practices
- Use claude-bot for well-defined tasks only
- Use direct @claude for exploration/discussion (cheaper)
- Review generated code before running (avoid wasted API calls)

---

## 8. Examples

### Example 1: Feature Discussion → Implementation
```markdown
# GitHub Issue #42: "Add dependency freshness assessor"

@claude What's the best way to check if dependencies are up-to-date?

[Claude responds with options: pip-audit, safety, custom parser]

Thanks! Let's use pip-audit. Assigning to @claude-bot for implementation.

[Assigns issue to claude-bot]
[claude-bot creates PR with pip-audit integration]
```

### Example 2: Code Review
```markdown
# PR #43: "Implement dependency freshness assessor"

@claude Can you review this implementation for security issues?

[Claude provides detailed security review in comment]
```

### Example 3: Quick Implementation
```markdown
# GitHub Issue #44: "Fix typo in README"

[Assigns to claude-bot immediately]
[claude-bot fixes typo in 30 seconds]
```

---

## 9. References

- **Claude Code Action**: https://github.com/anthropics/claude-code-action
- **Claude GitHub App**: https://github.com/apps/claude-ai
- **CLAUDE.md Best Practices**: https://arize.com/blog/claude-md-best-practices
- **AgentReady CLAUDE.md**: `/CLAUDE.md` (this repository)
- **Automation Prompt**: `/.github/claude-bot-prompt.md` (this repository)

---

**Last Updated**: 2025-11-21
**Maintained By**: @jeder
**Status**: Active
