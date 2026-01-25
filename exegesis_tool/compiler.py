"""Compile perspective results into markdown output."""

from typing import List, Dict

from .models import Passage, PerspectiveResult, PerspectiveStatus
from .prompts import get_prompt_module, PERSPECTIVES


# Section order for output
SECTION_ORDER = [
    "historian",
    "linguist",
    "author",
    "theologian",
    "disciple",
    "shepherd",
]


def compile_perspectives(
    passage: Passage,
    results: List[PerspectiveResult],
) -> str:
    """Compile all perspective results into a single markdown document.

    Args:
        passage: The passage that was analyzed
        results: List of PerspectiveResult objects

    Returns:
        Compiled markdown string
    """
    # Index results by perspective name
    results_by_name: Dict[str, PerspectiveResult] = {
        r.perspective: r for r in results
    }

    # Build document
    lines = []

    # Title
    title = f"# Exegetical Analysis of {passage.reference}"
    if passage.description:
        title += f" - {passage.description}"
    lines.append(title)
    lines.append("")

    # Add each section in order
    for perspective in SECTION_ORDER:
        prompt_module = get_prompt_module(perspective)
        section_title = prompt_module.SECTION_TITLE

        lines.append(f"## {section_title}")
        lines.append("")

        if perspective in results_by_name:
            result = results_by_name[perspective]
            if result.status == PerspectiveStatus.COMPLETED and result.content:
                # Clean up the content - remove any duplicate section headers
                content = _clean_content(result.content, section_title)
                lines.append(content)
            else:
                lines.append(f"*Analysis failed: {result.error_message or 'Unknown error'}*")
        else:
            lines.append("*Analysis not available*")

        lines.append("")
        lines.append("---")
        lines.append("")

    # Remove trailing separator
    while lines and lines[-1] in ("", "---"):
        lines.pop()

    return "\n".join(lines)


def _clean_content(content: str, section_title: str) -> str:
    """Clean up perspective content before including in compiled document.

    - Remove duplicate section headers if the API included them
    - Normalize heading levels
    - Strip leading/trailing whitespace
    """
    content = content.strip()

    # Remove section title if it appears at the start (API might have included it)
    for prefix in [f"## {section_title}", f"# {section_title}", section_title]:
        if content.lower().startswith(prefix.lower()):
            content = content[len(prefix):].strip()
            break

    # Ensure subsection headings are ### level (not ## or #)
    lines = content.split("\n")
    cleaned_lines = []

    for line in lines:
        # Convert ## to ### for subsections
        if line.startswith("## ") and not line.startswith("### "):
            line = "#" + line
        # Convert # to ### for what should be subsections
        elif line.startswith("# ") and not line.startswith("## "):
            line = "##" + line
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def compile_summary(results: List[PerspectiveResult]) -> str:
    """Generate a summary of the processing results.

    Args:
        results: List of PerspectiveResult objects

    Returns:
        Summary string
    """
    total = len(results)
    completed = sum(1 for r in results if r.status == PerspectiveStatus.COMPLETED)
    failed = sum(1 for r in results if r.status == PerspectiveStatus.FAILED)

    total_tokens = sum(r.total_tokens for r in results)
    total_duration = sum(r.duration_ms for r in results)

    lines = [
        f"Perspectives: {completed}/{total} completed",
    ]

    if failed > 0:
        failed_names = [r.perspective for r in results if r.status == PerspectiveStatus.FAILED]
        lines.append(f"Failed: {', '.join(failed_names)}")

    lines.append(f"Total tokens: {total_tokens:,}")
    lines.append(f"Total duration: {total_duration / 1000:.1f}s")

    return "\n".join(lines)
