"""JSON reporter for generating machine-readable assessment reports."""

import json
from pathlib import Path

from ..models.assessment import Assessment
from .base import BaseReporter


class JSONReporter(BaseReporter):
    """Generates JSON reports from individual assessments.

    Features:
    - Schema versioning for backwards compatibility
    - Complete assessment data including findings and remediation
    - Machine-readable for automation and tooling
    - ISO 8601 timestamps for unambiguous dates
    """

    def generate(self, assessment: Assessment, output_path: Path) -> Path:
        """Generate JSON report from assessment data.

        Args:
            assessment: Complete assessment with findings
            output_path: Path where JSON file should be saved

        Returns:
            Path to generated JSON file

        Raises:
            IOError: If JSON cannot be written
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(assessment.to_dict(), f, indent=2, default=str)

        return output_path
