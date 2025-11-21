"""Repomix configuration assessor."""

from ..models.attribute import Attribute
from ..models.finding import Finding
from ..models.repository import Repository
from ..services.repomix import RepomixService
from .base import BaseAssessor


class RepomixConfigAssessor(BaseAssessor):
    """Assesses Repomix configuration and freshness.

    Repomix generates AI-friendly repository context files, making it easier
    for LLMs to understand the codebase structure and contents.
    """

    @property
    def attribute_id(self) -> str:
        """Return attribute identifier."""
        return "repomix_config"

    @property
    def tier(self) -> int:
        """Return tier (3 = Important but not critical)."""
        return 3

    @property
    def attribute(self) -> Attribute:
        """Return attribute definition."""
        return Attribute(
            id=self.attribute_id,
            name="Repomix AI Context Generation",
            category="AI-Assisted Development Tools",
            tier=self.tier,
            description="Automated repository context generation for AI consumption",
            criteria="Repomix configured with fresh output (< 7 days old)",
            default_weight=0.02,
        )

    def assess(self, repository: Repository) -> Finding:
        """Assess Repomix configuration.

        Args:
            repository: Repository to assess

        Returns:
            Finding with assessment results
        """
        service = RepomixService(repository.path)

        # Check if Repomix is configured
        if not service.has_config():
            return Finding.create_fail(
                self.attribute,
                score=0,
                evidence=[
                    "Repomix configuration not found",
                    "Missing repomix.config.json",
                ],
                remediation_steps=[
                    "Initialize Repomix: agentready repomix-generate --init",
                    "Generate context: agentready repomix-generate",
                    "Add to bootstrap: agentready bootstrap --repomix",
                    "Set up GitHub Action for automatic updates",
                ],
                tools=["Repomix", "AgentReady"],
                commands=[
                    "agentready repomix-generate --init",
                    "agentready repomix-generate",
                ],
                examples=[
                    "# Initialize Repomix configuration\n"
                    "agentready repomix-generate --init\n\n"
                    "# Generate repository context\n"
                    "agentready repomix-generate\n\n"
                    "# Check freshness\n"
                    "agentready repomix-generate --check"
                ],
                citations=[
                    {
                        "title": "Repomix - AI-Friendly Repository Packager",
                        "url": "https://github.com/yamadashy/repomix",
                        "type": "tool",
                    }
                ],
            )

        # Check if output exists and is fresh
        output_files = service.get_output_files()
        if not output_files:
            return Finding.create_fail(
                self.attribute,
                score=50,
                evidence=[
                    "Repomix configuration exists",
                    "No Repomix output files found",
                ],
                remediation_steps=[
                    "Generate Repomix output: agentready repomix-generate",
                    "Commit output if needed for team access",
                    "Set up GitHub Action for automatic regeneration",
                ],
                tools=["Repomix"],
                commands=["agentready repomix-generate"],
            )

        # Check freshness (7 days max age)
        is_fresh, message = service.check_freshness(max_age_days=7)

        if is_fresh:
            # All good - config exists, output exists and is fresh
            return Finding.create_pass(
                self.attribute,
                score=100,
                evidence=[
                    "Repomix configuration exists",
                    f"{len(output_files)} output file(s) found",
                    message,
                ],
            )
        else:
            # Config exists, output exists but is stale
            return Finding.create_fail(
                self.attribute,
                score=75,
                evidence=[
                    "Repomix configuration exists",
                    f"{len(output_files)} output file(s) found",
                    message,
                ],
                remediation_steps=[
                    "Regenerate Repomix output: agentready repomix-generate",
                    "Set up GitHub Action for automatic weekly updates",
                    "Add to pre-commit hooks for automatic regeneration",
                ],
                tools=["Repomix"],
                commands=["agentready repomix-generate"],
            )
