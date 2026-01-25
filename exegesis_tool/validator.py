"""Output validation for compiled exegesis documents."""

import re
from dataclasses import dataclass, field
from typing import List

from .prompts import get_prompt_module, PERSPECTIVES


@dataclass
class ValidationResult:
    """Result of validating a compiled document."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        if self.is_valid:
            lines.append("Validation: PASSED")
        else:
            lines.append("Validation: FAILED")

        if self.errors:
            lines.append(f"Errors ({len(self.errors)}):")
            for error in self.errors:
                lines.append(f"  - {error}")

        if self.warnings:
            lines.append(f"Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                lines.append(f"  - {warning}")

        return "\n".join(lines)


# Expected section titles
REQUIRED_SECTIONS = [
    get_prompt_module(p).SECTION_TITLE for p in PERSPECTIVES
]

# Minimum character count per section to be considered "substantial"
MIN_SECTION_CHARS = 500


def validate_compiled_output(content: str) -> ValidationResult:
    """Validate that compiled markdown has all required sections with content.

    Args:
        content: Compiled markdown string

    Returns:
        ValidationResult with errors and warnings
    """
    errors = []
    warnings = []

    # Check for required sections
    for section in REQUIRED_SECTIONS:
        if f"## {section}" not in content:
            errors.append(f"Missing required section: {section}")

    # Split into sections and check content
    sections = _split_sections(content)

    for section_title, section_content in sections.items():
        # Check for empty sections
        if not section_content.strip():
            errors.append(f"Section '{section_title}' is empty")
            continue

        # Check for minimal content
        if len(section_content) < MIN_SECTION_CHARS:
            warnings.append(
                f"Section '{section_title}' has minimal content ({len(section_content)} chars)"
            )

        # Check for error markers
        if "*Analysis failed:" in section_content or "*Analysis not available*" in section_content:
            errors.append(f"Section '{section_title}' contains error marker")

        # Check for subsections (### headers)
        subsection_count = section_content.count("### ")
        if subsection_count == 0:
            warnings.append(f"Section '{section_title}' has no subsections")

        # Check for empty subsections
        empty_subsections = re.findall(r"###[^\n]+\n\s*(?=###|##|$)", section_content)
        if empty_subsections:
            warnings.append(f"Section '{section_title}' has {len(empty_subsections)} empty subsection(s)")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def _split_sections(content: str) -> dict:
    """Split content into sections by ## headers.

    Returns:
        Dict mapping section title to section content
    """
    sections = {}
    current_title = None
    current_content = []

    for line in content.split("\n"):
        if line.startswith("## "):
            # Save previous section
            if current_title:
                sections[current_title] = "\n".join(current_content)

            # Start new section
            current_title = line[3:].strip()
            current_content = []
        elif current_title:
            current_content.append(line)

    # Save last section
    if current_title:
        sections[current_title] = "\n".join(current_content)

    return sections


def validate_perspective_content(perspective: str, content: str) -> ValidationResult:
    """Validate content from a single perspective.

    Args:
        perspective: Perspective name
        content: Raw content from API

    Returns:
        ValidationResult with errors and warnings
    """
    errors = []
    warnings = []

    prompt_module = get_prompt_module(perspective)
    expected_questions = prompt_module.QUESTIONS

    # Check for each expected question as a subsection
    for question in expected_questions:
        # Look for the question as a heading (with or without "###")
        question_pattern = re.escape(question.rstrip("?"))
        if not re.search(f"###?\\s*{question_pattern}", content, re.IGNORECASE):
            warnings.append(f"Missing expected subsection: {question}")

    # Check minimum content length
    if len(content) < 500:
        warnings.append(f"Content is very short ({len(content)} chars)")

    # Check for markdown formatting
    if "###" not in content and "**" not in content:
        warnings.append("Content appears to lack markdown formatting")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
