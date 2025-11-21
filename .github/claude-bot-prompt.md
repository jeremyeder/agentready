# Claude Bot Automation Context

This file provides additional instructions for the automated Claude Code Action when implementing issues assigned to `claude-bot`.

## Automation Workflow

When assigned an issue, you should:

1. **Create feature branch**: Always create a feature branch from `main` (never push to main directly)
2. **Follow TDD**: Write tests before implementation when applicable
3. **Run linters**: Always run `black`, `isort`, `ruff` before committing
4. **Run tests**: Ensure all tests pass with `pytest`
5. **Commit frequently**: Use conventional commits with clear, succinct messages
6. **Open PR**: Create a pull request for review (don't merge automatically)

## Implementation Standards

- **Python**: Follow PEP 8, use type hints, support Python 3.11+
- **Testing**: Maintain >80% coverage for new code
- **Documentation**: Update docstrings and CLAUDE.md as needed
- **Security**: Never expose secrets, validate inputs, follow OWASP guidelines

## PR Template

When creating pull requests, include:
- Summary of changes
- Test plan
- Breaking changes (if any)
- Related issues/tickets

## Important Context

- This is an open-source project under MIT license
- Target audience: Software engineering teams using AI-assisted development
- Code quality and user experience are paramount
- Prefer simple, focused solutions over complex abstractions

---

**Note**: CLAUDE.md is automatically read by the action. This file provides automation-specific guidance that supplements the project-level instructions.
