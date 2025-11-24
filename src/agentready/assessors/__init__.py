"""Assessor factory for centralized assessor creation.

Phase 1 Task 3: Consolidated from duplicated create_all_assessors() functions
across CLI modules (main.py, assess_batch.py, demo.py).
"""

from .base import BaseAssessor
from .code_quality import (
    CodeSmellsAssessor,
    CyclomaticComplexityAssessor,
    SemanticNamingAssessor,
    StructuredLoggingAssessor,
    TypeAnnotationsAssessor,
)
from .documentation import (
    ArchitectureDecisionsAssessor,
    CLAUDEmdAssessor,
    ConciseDocumentationAssessor,
    InlineDocumentationAssessor,
    OpenAPISpecsAssessor,
    READMEAssessor,
)
from .structure import (
    IssuePRTemplatesAssessor,
    OneCommandSetupAssessor,
    SeparationOfConcernsAssessor,
    StandardLayoutAssessor,
)
from .stub_assessors import (
    ConventionalCommitsAssessor,
    GitignoreAssessor,
    LockFilesAssessor,
    create_stub_assessors,
)
from .testing import (
    BranchProtectionAssessor,
    CICDPipelineVisibilityAssessor,
    PreCommitHooksAssessor,
    TestCoverageAssessor,
)

__all__ = ["create_all_assessors", "BaseAssessor"]


def create_all_assessors() -> list[BaseAssessor]:
    """Create all 25 assessors for assessment.

    Centralized factory function to eliminate duplication across CLI commands.
    Returns all implemented and stub assessors.

    Returns:
        List of all assessor instances
    """
    assessors = [
        # Tier 1 Essential (5 assessors)
        CLAUDEmdAssessor(),
        READMEAssessor(),
        TypeAnnotationsAssessor(),
        StandardLayoutAssessor(),
        LockFilesAssessor(),
        # Tier 2 Critical (10 assessors - 6 implemented, 4 stubs)
        TestCoverageAssessor(),
        PreCommitHooksAssessor(),
        ConventionalCommitsAssessor(),
        GitignoreAssessor(),
        OneCommandSetupAssessor(),
        SeparationOfConcernsAssessor(),
        ConciseDocumentationAssessor(),
        InlineDocumentationAssessor(),
        CyclomaticComplexityAssessor(),  # Actually Tier 3, but including here
        # Tier 3 Important (7 implemented)
        ArchitectureDecisionsAssessor(),
        IssuePRTemplatesAssessor(),
        CICDPipelineVisibilityAssessor(),
        SemanticNamingAssessor(),
        StructuredLoggingAssessor(),
        OpenAPISpecsAssessor(),
        # Tier 4 Advanced (2 stubs)
        BranchProtectionAssessor(),
        CodeSmellsAssessor(),
    ]

    # Add remaining stub assessors
    assessors.extend(create_stub_assessors())

    return assessors
