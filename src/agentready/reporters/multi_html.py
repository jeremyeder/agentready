"""Multi-repository HTML reporter for batch assessment summaries.

SECURITY: Implements comprehensive XSS prevention through:
- Jinja2 autoescape
- URL validation and sanitization
- Content Security Policy headers
"""

import html
from pathlib import Path
from urllib.parse import urlparse

import jinja2

from ..models.batch_assessment import BatchAssessment


class MultiRepoHTMLReporter:
    """Generates summary HTML report for batch assessments.

    SECURITY REQUIREMENTS:
    - Jinja2 autoescape MUST be enabled (prevents XSS)
    - All repository metadata MUST be HTML-escaped
    - CSP header MUST be included (prevents script injection)
    - URLs MUST be validated (only http/https allowed)

    References:
    - OWASP XSS Prevention: https://owasp.org/www-community/attacks/xss/
    - CWE-79: Improper Neutralization of Input During Web Page Generation
    """

    def __init__(self, template_dir: Path):
        """Initialize reporter with Jinja2 environment.

        Args:
            template_dir: Directory containing Jinja2 templates

        SECURITY: Autoescape is ENABLED by default for HTML/XML files.
        """
        # SECURITY: Enable autoescape to prevent XSS
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            autoescape=jinja2.select_autoescape(["html", "xml", "j2"]),
        )

        # Register security filters
        self.env.filters["sanitize_url"] = self.sanitize_url

    @staticmethod
    def sanitize_url(url: str) -> str:
        """Validate and sanitize URLs for safe HTML rendering.

        SECURITY: Only allow http/https schemes. Prevents javascript:,
        data:, file:, and other potentially malicious URL schemes.

        Args:
            url: URL to sanitize

        Returns:
            HTML-escaped URL if valid, empty string otherwise

        Examples:
            >>> MultiRepoHTMLReporter.sanitize_url("https://github.com/user/repo")
            "https://github.com/user/repo"
            >>> MultiRepoHTMLReporter.sanitize_url("javascript:alert(1)")
            ""
        """
        if not url:
            return ""

        try:
            parsed = urlparse(url)
            # SECURITY: Only allow http/https schemes
            if parsed.scheme not in ("http", "https", ""):
                return ""
            # SECURITY: HTML-escape the URL to prevent attribute injection
            return html.escape(url, quote=True)
        except Exception:
            # Failed to parse - treat as unsafe
            return ""

    def generate(self, batch_assessment: BatchAssessment, output_path: Path) -> Path:
        """Generate summary HTML report for batch assessment.

        Args:
            batch_assessment: Complete batch assessment with all results
            output_path: Path where HTML file should be saved

        Returns:
            Path to generated HTML file

        Raises:
            IOError: If HTML cannot be written
        """
        template = self.env.get_template("multi_report.html.j2")

        # Render template with assessment data
        # SECURITY: Jinja2 autoescape handles all variable escaping
        html_content = template.render(
            batch_assessment=batch_assessment,
            timestamp=batch_assessment.timestamp.isoformat(),
        )

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding="utf-8")

        return output_path
