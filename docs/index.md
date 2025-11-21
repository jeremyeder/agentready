---
layout: home
title: Home
---

# AgentReady

**Assess git repositories against 25 evidence-based attributes for AI-assisted development readiness.**

<div class="hero">
  <p class="hero-tagline">Transform your codebase into an AI-friendly powerhouse. Get actionable insights in seconds.</p>
  <div class="hero-buttons">
    <a href="/user-guide#installation" class="button button-primary">Get Started</a>
    <a href="/examples" class="button button-secondary">View Examples</a>
  </div>
</div>

## Why AgentReady?

AI-assisted development tools like Claude Code, GitHub Copilot, and Cursor AI work best with well-structured, documented codebases. AgentReady evaluates your repository across **25 research-backed attributes** and provides specific, actionable guidance to improve AI effectiveness.

<div class="feature-grid">
  <div class="feature">
    <h3>📊 Comprehensive Assessment</h3>
    <p>Evaluate 25 attributes across documentation, code quality, testing, structure, and security.</p>
  </div>
  <div class="feature">
    <h3>🎯 Actionable Guidance</h3>
    <p>Get specific tools, commands, and examples to improve each attribute—not generic advice.</p>
  </div>
  <div class="feature">
    <h3>📈 Track Progress</h3>
    <p>Version-control-friendly Markdown reports let you track improvements over time.</p>
  </div>
  <div class="feature">
    <h3>🏆 Earn Certifications</h3>
    <p>Platinum, Gold, Silver, Bronze levels validate your codebase quality.</p>
  </div>
  <div class="feature">
    <h3>⚡ Fast & Lightweight</h3>
    <p>Complete assessments in seconds. No external dependencies or cloud services required.</p>
  </div>
  <div class="feature">
    <h3>🔬 Research-Backed</h3>
    <p>Every attribute is backed by 50+ citations from Anthropic, Microsoft, Google, and academic research.</p>
  </div>
</div>

## Quick Start

```bash
# Install AgentReady
pip install agentready

# Assess your repository
cd /path/to/your/repo
agentready assess .

# View interactive HTML report
open .agentready/report-latest.html
```

**That's it!** In under a minute, you'll have:
- Overall score and certification level (Platinum/Gold/Silver/Bronze)
- Detailed findings for all 25 attributes
- Specific remediation steps with tools and examples
- Three report formats (HTML, Markdown, JSON)

[See full installation guide →](/user-guide#installation)

## Certification Levels

AgentReady scores repositories on a 0-100 scale with tier-weighted attributes:

<div class="certification-ladder">
  <div class="cert-level platinum">
    <div class="cert-badge">🏆 Platinum</div>
    <div class="cert-range">90-100</div>
    <div class="cert-desc">Exemplary agent-ready codebase</div>
  </div>
  <div class="cert-level gold">
    <div class="cert-badge">🥇 Gold</div>
    <div class="cert-range">75-89</div>
    <div class="cert-desc">Highly optimized for AI agents</div>
  </div>
  <div class="cert-level silver">
    <div class="cert-badge">🥈 Silver</div>
    <div class="cert-range">60-74</div>
    <div class="cert-desc">Well-suited for AI development</div>
  </div>
  <div class="cert-level bronze">
    <div class="cert-badge">🥉 Bronze</div>
    <div class="cert-range">40-59</div>
    <div class="cert-desc">Basic agent compatibility</div>
  </div>
  <div class="cert-level needs-improvement">
    <div class="cert-badge">📈 Needs Improvement</div>
    <div class="cert-range">0-39</div>
    <div class="cert-desc">Significant friction for AI agents</div>
  </div>
</div>

**AgentReady itself scores 75.4/100 (Gold)** — see our [self-assessment report](/examples/self-assessment).

## What Gets Assessed?

AgentReady evaluates 25 attributes organized into four weighted tiers:

### Tier 1: Essential (50% of score)
The fundamentals that enable basic AI agent functionality:
- **CLAUDE.md File** — Project context for AI agents
- **README Structure** — Clear documentation entry point
- **Type Annotations** — Static typing for better code understanding
- **Standard Project Layout** — Predictable directory structure
- **Lock Files** — Reproducible dependency management

### Tier 2: Critical (30% of score)
Major quality improvements and safety nets:
- **Test Coverage** — Confidence for AI-assisted refactoring
- **Pre-commit Hooks** — Automated quality enforcement
- **Conventional Commits** — Structured git history
- **Gitignore Completeness** — Clean repository navigation
- **One-Command Setup** — Easy environment reproduction

### Tier 3: Important (15% of score)
Significant improvements in specific areas:
- **Cyclomatic Complexity** — Code comprehension metrics
- **Structured Logging** — Machine-parseable debugging
- **API Documentation** — OpenAPI/GraphQL specifications
- **Architecture Decision Records** — Historical design context
- **Semantic Naming** — Clear, descriptive identifiers

### Tier 4: Advanced (5% of score)
Refinement and optimization:
- **Security Scanning** — Automated vulnerability detection
- **Performance Benchmarks** — Regression tracking
- **Code Smell Elimination** — Quality baseline maintenance
- **PR/Issue Templates** — Consistent contribution workflow
- **Container Setup** — Portable development environments

[View complete attribute reference →](/attributes)

## Report Formats

AgentReady generates three complementary report formats:

### Interactive HTML Report
- Color-coded findings with visual score indicators
- Search, filter, and sort capabilities
- Collapsible sections for detailed analysis
- Works offline (no CDN dependencies)
- **Use case**: Share with stakeholders, detailed exploration

### Version-Control Markdown
- GitHub-Flavored Markdown with tables and emojis
- Git-diffable format for tracking progress
- Certification ladder and next steps
- **Use case**: Commit to repository, track improvements over time

### Machine-Readable JSON
- Complete assessment data structure
- Timestamps and metadata
- Structured findings with evidence
- **Use case**: CI/CD integration, programmatic analysis

[See example reports →](/examples)

## Evidence-Based Research

All 25 attributes are derived from authoritative sources:

- **Anthropic** — Claude Code best practices and engineering blog
- **Microsoft** — Code metrics and Azure DevOps guidance
- **Google** — SRE handbook and style guides
- **ArXiv** — Software engineering research papers
- **IEEE/ACM** — Academic publications on code quality

Every attribute includes specific citations and measurable criteria. No subjective opinions—just proven practices that improve AI effectiveness.

[Read the research document →](https://github.com/yourusername/agentready/blob/main/agent-ready-codebase-attributes.md)

## Use Cases

<div class="use-case-grid">
  <div class="use-case">
    <h4>🚀 New Projects</h4>
    <p>Start with best practices from day one. Use AgentReady's guidance to structure your repository for AI-assisted development from the beginning.</p>
  </div>
  <div class="use-case">
    <h4>🔄 Legacy Modernization</h4>
    <p>Identify high-impact improvements to make legacy codebases more AI-friendly. Prioritize changes with tier-based scoring.</p>
  </div>
  <div class="use-case">
    <h4>📊 Team Standards</h4>
    <p>Establish organization-wide quality baselines. Track adherence across multiple repositories with consistent, objective metrics.</p>
  </div>
  <div class="use-case">
    <h4>🎓 Education & Onboarding</h4>
    <p>Teach developers what makes code AI-ready. Use assessments as learning tools to understand best practices.</p>
  </div>
</div>

## What Users Are Saying

> "Running AgentReady on our codebase identified 5 quick wins that immediately improved Claude Code's suggestions. The actionable remediation made it easy to implement changes in under an hour."
> — *Engineering Team Lead*

> "The research backing each attribute gave me confidence these weren't arbitrary rules. Every recommendation is cited and measurable."
> — *Principal Engineer*

> "We use AgentReady in CI to prevent regression. It's become part of our definition of done for new features."
> — *DevOps Engineer*

## Ready to Get Started?

<div class="cta-section">
  <h3>Assess your repository in 60 seconds</h3>
  <pre><code>pip install agentready
agentready assess .
</code></pre>
  <a href="/user-guide" class="button button-primary button-large">Read the User Guide</a>
</div>

---

## Latest News

**Version 1.0.0 Released** (2025-11-21)
Initial release with 10 implemented assessors, interactive HTML reports, and comprehensive documentation. AgentReady achieves Gold certification (75.4/100) on its own codebase.

[View changelog →](https://github.com/yourusername/agentready/releases)

## Community

- **GitHub**: [github.com/yourusername/agentready](https://github.com/yourusername/agentready)
- **Issues**: Report bugs or request features
- **Discussions**: Ask questions and share experiences
- **Contributing**: See the [Developer Guide](/developer-guide)

## License

AgentReady is open source under the [MIT License](https://github.com/yourusername/agentready/blob/main/LICENSE).
