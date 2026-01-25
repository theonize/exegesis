"""Data models for exegesis tool."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class PassageStatus(str, Enum):
    """Status of a passage in the processing pipeline."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class PerspectiveStatus(str, Enum):
    """Status of a single perspective run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Passage:
    """A Bible passage to be analyzed."""
    book: str
    chapter: int
    verse_start: int
    verse_end: int
    description: str = ""
    status: PassageStatus = PassageStatus.PENDING
    output_path: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def reference(self) -> str:
        """Get the passage reference string (e.g., 'GEN 01:26-31')."""
        return f"{self.book} {self.chapter:02d}:{self.verse_start}-{self.verse_end}"

    @property
    def filename(self) -> str:
        """Get the output filename (e.g., 'GEN_01_26-31.md')."""
        return f"{self.book}_{self.chapter:02d}_{self.verse_start}-{self.verse_end}.md"

    @property
    def output_dir(self) -> str:
        """Get the output directory path (e.g., 'content/GEN/01')."""
        return f"content/{self.book}/{self.chapter:02d}"

    @classmethod
    def from_reference(cls, reference: str, description: str = "") -> "Passage":
        """Parse a passage reference string (e.g., 'GEN 01:26-31')."""
        import re
        match = re.match(r"([A-Z]{3})\s*(\d+):(\d+)-(\d+)", reference)
        if not match:
            raise ValueError(f"Invalid passage reference: {reference}")
        book, chapter, v_start, v_end = match.groups()
        return cls(
            book=book,
            chapter=int(chapter),
            verse_start=int(v_start),
            verse_end=int(v_end),
            description=description,
        )


@dataclass
class PerspectiveResult:
    """Result of running a single perspective analysis."""
    perspective: str
    status: PerspectiveStatus
    content: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0
    error_message: str = ""
    attempt_number: int = 1
    id: Optional[int] = None
    passage_id: Optional[int] = None
    created_at: Optional[datetime] = None

    @property
    def is_success(self) -> bool:
        """Check if this perspective completed successfully."""
        return self.status == PerspectiveStatus.COMPLETED

    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output)."""
        return self.input_tokens + self.output_tokens


@dataclass
class CompilationResult:
    """Result of compiling all perspectives into a single document."""
    passage: Passage
    perspectives: List[PerspectiveResult]
    compiled_content: str = ""
    is_complete: bool = False
    failed_perspectives: List[str] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        """Number of successful perspective analyses."""
        return sum(1 for p in self.perspectives if p.is_success)

    @property
    def total_tokens(self) -> int:
        """Total tokens used across all perspectives."""
        return sum(p.total_tokens for p in self.perspectives)

    @property
    def total_duration_ms(self) -> int:
        """Total duration across all perspectives."""
        return sum(p.duration_ms for p in self.perspectives)


@dataclass
class BatchRun:
    """A batch processing run."""
    id: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_passages: int = 0
    completed_passages: int = 0
    failed_passages: int = 0
    status: str = "running"


@dataclass
class StatusSummary:
    """Summary of passage processing status."""
    pending: int = 0
    in_progress: int = 0
    completed: int = 0
    failed: int = 0

    @property
    def total(self) -> int:
        return self.pending + self.in_progress + self.completed + self.failed

    def __str__(self) -> str:
        return (
            f"Pending:     {self.pending}\n"
            f"In Progress: {self.in_progress}\n"
            f"Completed:   {self.completed}\n"
            f"Failed:      {self.failed}\n"
            f"Total:       {self.total}"
        )
