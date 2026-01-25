"""SQLite database operations for exegesis tool."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from contextlib import contextmanager

from .models import (
    Passage, PassageStatus, PerspectiveResult, PerspectiveStatus,
    StatusSummary, BatchRun
)


SCHEMA = """
CREATE TABLE IF NOT EXISTS passages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse_start INTEGER NOT NULL,
    verse_end INTEGER NOT NULL,
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'pending',
    output_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(book, chapter, verse_start, verse_end)
);

CREATE TABLE IF NOT EXISTS perspective_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    passage_id INTEGER NOT NULL REFERENCES passages(id),
    perspective TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    content TEXT DEFAULT '',
    error_message TEXT DEFAULT '',
    attempt_number INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS batch_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    total_passages INTEGER DEFAULT 0,
    completed_passages INTEGER DEFAULT 0,
    failed_passages INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running'
);

CREATE INDEX IF NOT EXISTS idx_passages_status ON passages(status);
CREATE INDEX IF NOT EXISTS idx_passages_book ON passages(book);
CREATE INDEX IF NOT EXISTS idx_perspective_runs_passage ON perspective_runs(passage_id);
CREATE INDEX IF NOT EXISTS idx_perspective_runs_status ON perspective_runs(status);
"""


class Database:
    """SQLite database for tracking exegesis processing state."""

    def __init__(self, db_path: str = "exegesis.db"):
        self.db_path = Path(db_path)
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema."""
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # --- Passage Operations ---

    def upsert_passage(self, passage: Passage) -> int:
        """Insert or update a passage. Returns the passage ID."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO passages (book, chapter, verse_start, verse_end, description, status, output_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(book, chapter, verse_start, verse_end) DO UPDATE SET
                    description = excluded.description,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
                """,
                (
                    passage.book,
                    passage.chapter,
                    passage.verse_start,
                    passage.verse_end,
                    passage.description,
                    passage.status.value if isinstance(passage.status, PassageStatus) else passage.status,
                    passage.output_path,
                ),
            )
            row = cursor.fetchone()
            return row["id"]

    def get_passage(self, passage_id: int) -> Optional[Passage]:
        """Get a passage by ID."""
        with self._connect() as conn:
            cursor = conn.execute("SELECT * FROM passages WHERE id = ?", (passage_id,))
            row = cursor.fetchone()
            return self._row_to_passage(row) if row else None

    def get_passage_by_reference(self, book: str, chapter: int, verse_start: int, verse_end: int) -> Optional[Passage]:
        """Get a passage by its reference."""
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM passages WHERE book = ? AND chapter = ? AND verse_start = ? AND verse_end = ?",
                (book, chapter, verse_start, verse_end),
            )
            row = cursor.fetchone()
            return self._row_to_passage(row) if row else None

    def get_pending_passages(self, limit: int = 10, book: Optional[str] = None) -> List[Passage]:
        """Get pending passages, optionally filtered by book."""
        with self._connect() as conn:
            if book:
                cursor = conn.execute(
                    "SELECT * FROM passages WHERE status = 'pending' AND book = ? ORDER BY book, chapter, verse_start LIMIT ?",
                    (book, limit),
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM passages WHERE status = 'pending' ORDER BY book, chapter, verse_start LIMIT ?",
                    (limit,),
                )
            return [self._row_to_passage(row) for row in cursor.fetchall()]

    def get_failed_passages(self, limit: int = 100) -> List[Passage]:
        """Get failed passages."""
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM passages WHERE status = 'failed' ORDER BY book, chapter, verse_start LIMIT ?",
                (limit,),
            )
            return [self._row_to_passage(row) for row in cursor.fetchall()]

    def update_passage_status(self, passage_id: int, status: PassageStatus, output_path: Optional[str] = None):
        """Update passage status."""
        with self._connect() as conn:
            if output_path:
                conn.execute(
                    "UPDATE passages SET status = ?, output_path = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (status.value, output_path, passage_id),
                )
            else:
                conn.execute(
                    "UPDATE passages SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (status.value, passage_id),
                )

    def claim_passages(self, passage_ids: List[int]) -> int:
        """Atomically claim multiple passages for processing. Returns count claimed."""
        with self._connect() as conn:
            placeholders = ",".join("?" * len(passage_ids))
            cursor = conn.execute(
                f"""
                UPDATE passages
                SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP
                WHERE id IN ({placeholders}) AND status = 'pending'
                """,
                passage_ids,
            )
            return cursor.rowcount

    def _row_to_passage(self, row: sqlite3.Row) -> Passage:
        """Convert a database row to a Passage object."""
        return Passage(
            id=row["id"],
            book=row["book"],
            chapter=row["chapter"],
            verse_start=row["verse_start"],
            verse_end=row["verse_end"],
            description=row["description"] or "",
            status=PassageStatus(row["status"]),
            output_path=row["output_path"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
        )

    # --- Perspective Run Operations ---

    def save_perspective_run(self, passage_id: int, result: PerspectiveResult) -> int:
        """Save a perspective run result. Returns the run ID."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO perspective_runs
                (passage_id, perspective, status, input_tokens, output_tokens, duration_ms, content, error_message, attempt_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
                """,
                (
                    passage_id,
                    result.perspective,
                    result.status.value if isinstance(result.status, PerspectiveStatus) else result.status,
                    result.input_tokens,
                    result.output_tokens,
                    result.duration_ms,
                    result.content,
                    result.error_message,
                    result.attempt_number,
                ),
            )
            row = cursor.fetchone()
            return row["id"]

    def get_perspective_runs(self, passage_id: int) -> List[PerspectiveResult]:
        """Get all perspective runs for a passage."""
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM perspective_runs WHERE passage_id = ? ORDER BY perspective, attempt_number DESC",
                (passage_id,),
            )
            return [self._row_to_perspective_result(row) for row in cursor.fetchall()]

    def get_latest_perspective_runs(self, passage_id: int) -> List[PerspectiveResult]:
        """Get the latest run for each perspective of a passage."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT pr.* FROM perspective_runs pr
                INNER JOIN (
                    SELECT perspective, MAX(id) as max_id
                    FROM perspective_runs
                    WHERE passage_id = ?
                    GROUP BY perspective
                ) latest ON pr.id = latest.max_id
                ORDER BY pr.perspective
                """,
                (passage_id,),
            )
            return [self._row_to_perspective_result(row) for row in cursor.fetchall()]

    def get_failed_perspectives(self, passage_id: int) -> List[str]:
        """Get list of perspective names that failed for a passage."""
        runs = self.get_latest_perspective_runs(passage_id)
        return [r.perspective for r in runs if r.status == PerspectiveStatus.FAILED]

    def _row_to_perspective_result(self, row: sqlite3.Row) -> PerspectiveResult:
        """Convert a database row to a PerspectiveResult object."""
        return PerspectiveResult(
            id=row["id"],
            passage_id=row["passage_id"],
            perspective=row["perspective"],
            status=PerspectiveStatus(row["status"]),
            input_tokens=row["input_tokens"],
            output_tokens=row["output_tokens"],
            duration_ms=row["duration_ms"],
            content=row["content"],
            error_message=row["error_message"],
            attempt_number=row["attempt_number"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
        )

    # --- Status Operations ---

    def get_status_summary(self) -> StatusSummary:
        """Get summary of passage statuses."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT status, COUNT(*) as count
                FROM passages
                GROUP BY status
                """
            )
            summary = StatusSummary()
            for row in cursor.fetchall():
                status = row["status"]
                count = row["count"]
                if status == "pending":
                    summary.pending = count
                elif status == "in_progress":
                    summary.in_progress = count
                elif status == "completed":
                    summary.completed = count
                elif status == "failed":
                    summary.failed = count
            return summary

    def get_total_tokens_used(self) -> int:
        """Get total tokens used across all runs."""
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT COALESCE(SUM(input_tokens + output_tokens), 0) as total FROM perspective_runs"
            )
            row = cursor.fetchone()
            return row["total"]

    # --- Batch Operations ---

    def create_batch_run(self, total_passages: int) -> int:
        """Create a new batch run. Returns the batch ID."""
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO batch_runs (total_passages) VALUES (?) RETURNING id",
                (total_passages,),
            )
            row = cursor.fetchone()
            return row["id"]

    def update_batch_run(self, batch_id: int, completed: int = 0, failed: int = 0, status: Optional[str] = None):
        """Update batch run progress."""
        with self._connect() as conn:
            if status:
                conn.execute(
                    """
                    UPDATE batch_runs
                    SET completed_passages = completed_passages + ?,
                        failed_passages = failed_passages + ?,
                        status = ?,
                        completed_at = CASE WHEN ? IN ('completed', 'failed', 'cancelled') THEN CURRENT_TIMESTAMP ELSE completed_at END
                    WHERE id = ?
                    """,
                    (completed, failed, status, status, batch_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE batch_runs
                    SET completed_passages = completed_passages + ?,
                        failed_passages = failed_passages + ?
                    WHERE id = ?
                    """,
                    (completed, failed, batch_id),
                )
