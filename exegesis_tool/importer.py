"""Import and export passages from TODO.md format."""

import re
from pathlib import Path
from typing import List, Tuple

from .database import Database
from .models import Passage, PassageStatus


# Pattern: - [status] BOOK CH:V1-V2 - Description
# Examples:
#   - [✅] GEN 01:1-25 - Creation of the world
#   - [ ] GEN 02:1-3 - The seventh day rest
#   - [🔄] GEN 03:1-7 - The temptation and fall
PASSAGE_PATTERN = re.compile(
    r"^\s*-\s*\[([^\]]*)\]\s*"  # Status in brackets
    r"([A-Z]{2,3})\s+"  # Book code (2-3 letters)
    r"(\d+):(\d+)-(\d+)"  # Chapter:VerseStart-VerseEnd
    r"\s*-\s*(.+)$"  # Description
)

# Map status characters to PassageStatus
STATUS_MAP = {
    " ": PassageStatus.PENDING,
    "": PassageStatus.PENDING,
    "✅": PassageStatus.COMPLETED,
    "🔄": PassageStatus.IN_PROGRESS,
    "❌": PassageStatus.FAILED,
}

# Reverse map for export
STATUS_CHAR_MAP = {
    PassageStatus.PENDING: " ",
    PassageStatus.IN_PROGRESS: "🔄",
    PassageStatus.COMPLETED: "✅",
    PassageStatus.FAILED: "❌",
}


def import_from_todo(db: Database, todo_path: str) -> int:
    """Parse TODO.md and import passages into database.

    Args:
        db: Database instance
        todo_path: Path to TODO.md file

    Returns:
        Number of passages imported
    """
    imported = 0

    with open(todo_path, "r", encoding="utf-8") as f:
        for line in f:
            match = PASSAGE_PATTERN.match(line)
            if match:
                status_char, book, chapter, v_start, v_end, description = match.groups()

                # Map status character
                status_char = status_char.strip()
                status = STATUS_MAP.get(status_char, PassageStatus.PENDING)

                passage = Passage(
                    book=book,
                    chapter=int(chapter),
                    verse_start=int(v_start),
                    verse_end=int(v_end),
                    description=description.strip(),
                    status=status,
                )

                # Upsert into database
                db.upsert_passage(passage)
                imported += 1

    return imported


def export_to_todo(db: Database, todo_path: str) -> int:
    """Export passages from database to TODO.md format.

    Args:
        db: Database instance
        todo_path: Path to write TODO.md file

    Returns:
        Number of passages exported
    """
    # Get all passages grouped by book
    passages_by_book = _get_passages_by_book(db)

    lines = [
        "# Exegesis TODO - Biblical Text Sections",
        "",
        "❌  failed",
        "🔄  in progress",
        "✅  completed",
        "",
    ]

    # Book name mapping (can be extended)
    book_names = {
        "GEN": "Genesis",
        "EXO": "Exodus",
        "LEV": "Leviticus",
        "NUM": "Numbers",
        "DEU": "Deuteronomy",
        # Add more as needed
    }

    exported = 0
    for book_code in sorted(passages_by_book.keys()):
        passages = passages_by_book[book_code]
        book_name = book_names.get(book_code, book_code)

        lines.append(f"## {book_name} ({book_code})")
        lines.append("")

        # Sort by chapter and verse
        passages.sort(key=lambda p: (p.chapter, p.verse_start))

        for passage in passages:
            status_char = STATUS_CHAR_MAP.get(passage.status, " ")
            line = f"- [{status_char}] {passage.book} {passage.chapter:02d}:{passage.verse_start}-{passage.verse_end} - {passage.description}"
            lines.append(line)
            exported += 1

        lines.append("")

    # Write file
    Path(todo_path).write_text("\n".join(lines), encoding="utf-8")

    return exported


def _get_passages_by_book(db: Database) -> dict:
    """Get all passages grouped by book code."""
    passages_by_book = {}

    # Query all passages
    with db._connect() as conn:
        cursor = conn.execute("SELECT * FROM passages ORDER BY book, chapter, verse_start")
        for row in cursor.fetchall():
            passage = db._row_to_passage(row)
            if passage.book not in passages_by_book:
                passages_by_book[passage.book] = []
            passages_by_book[passage.book].append(passage)

    return passages_by_book


def parse_passage_reference(reference: str) -> Tuple[str, int, int, int]:
    """Parse a passage reference string.

    Args:
        reference: String like "GEN 01:26-31" or "GEN 1:26-31"

    Returns:
        Tuple of (book, chapter, verse_start, verse_end)

    Raises:
        ValueError: If reference cannot be parsed
    """
    match = re.match(r"([A-Z]{2,3})\s*(\d+):(\d+)-(\d+)", reference)
    if not match:
        raise ValueError(f"Invalid passage reference: {reference}")

    book, chapter, v_start, v_end = match.groups()
    return book, int(chapter), int(v_start), int(v_end)
