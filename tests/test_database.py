"""Tests for database module."""

import tempfile
import os
import pytest

from exegesis_tool.database import Database
from exegesis_tool.models import Passage, PassageStatus, PerspectiveResult, PerspectiveStatus


class TestDatabase:
    """Tests for Database class."""

    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = Database(self.db_path)

    def teardown_method(self):
        """Clean up temporary files."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_upsert_passage(self):
        """Test inserting and updating a passage."""
        passage = Passage(
            book="GEN",
            chapter=1,
            verse_start=1,
            verse_end=25,
            description="Creation of the world",
        )

        passage_id = self.db.upsert_passage(passage)
        assert passage_id > 0

        # Retrieve and verify
        retrieved = self.db.get_passage(passage_id)
        assert retrieved is not None
        assert retrieved.book == "GEN"
        assert retrieved.chapter == 1
        assert retrieved.verse_start == 1
        assert retrieved.verse_end == 25
        assert retrieved.description == "Creation of the world"
        assert retrieved.status == PassageStatus.PENDING

    def test_upsert_passage_updates_existing(self):
        """Test that upsert updates existing passage."""
        passage1 = Passage(
            book="GEN",
            chapter=1,
            verse_start=1,
            verse_end=25,
            description="Original description",
        )
        id1 = self.db.upsert_passage(passage1)

        passage2 = Passage(
            book="GEN",
            chapter=1,
            verse_start=1,
            verse_end=25,
            description="Updated description",
        )
        id2 = self.db.upsert_passage(passage2)

        # Should be same ID
        assert id1 == id2

        # Description should be updated
        retrieved = self.db.get_passage(id1)
        assert retrieved.description == "Updated description"

    def test_get_passage_by_reference(self):
        """Test getting passage by book/chapter/verses."""
        passage = Passage(
            book="EXO",
            chapter=3,
            verse_start=1,
            verse_end=12,
            description="Burning bush",
        )
        self.db.upsert_passage(passage)

        retrieved = self.db.get_passage_by_reference("EXO", 3, 1, 12)
        assert retrieved is not None
        assert retrieved.description == "Burning bush"

    def test_get_pending_passages(self):
        """Test getting pending passages."""
        passages = [
            Passage(book="GEN", chapter=1, verse_start=1, verse_end=25, description="A"),
            Passage(book="GEN", chapter=2, verse_start=1, verse_end=3, description="B"),
            Passage(book="GEN", chapter=3, verse_start=1, verse_end=7, description="C"),
        ]
        for p in passages:
            self.db.upsert_passage(p)

        pending = self.db.get_pending_passages(limit=2)
        assert len(pending) == 2

    def test_update_passage_status(self):
        """Test updating passage status."""
        passage = Passage(
            book="GEN",
            chapter=1,
            verse_start=1,
            verse_end=25,
        )
        passage_id = self.db.upsert_passage(passage)

        self.db.update_passage_status(passage_id, PassageStatus.COMPLETED, "content/GEN/01/GEN_01_1-25.md")

        retrieved = self.db.get_passage(passage_id)
        assert retrieved.status == PassageStatus.COMPLETED
        assert retrieved.output_path == "content/GEN/01/GEN_01_1-25.md"

    def test_claim_passages(self):
        """Test atomic claiming of passages."""
        passages = [
            Passage(book="GEN", chapter=1, verse_start=1, verse_end=25),
            Passage(book="GEN", chapter=2, verse_start=1, verse_end=3),
        ]
        ids = [self.db.upsert_passage(p) for p in passages]

        claimed = self.db.claim_passages(ids)
        assert claimed == 2

        # All should now be in_progress
        for pid in ids:
            p = self.db.get_passage(pid)
            assert p.status == PassageStatus.IN_PROGRESS

        # Claiming again should claim 0
        claimed = self.db.claim_passages(ids)
        assert claimed == 0

    def test_save_perspective_run(self):
        """Test saving perspective run results."""
        passage = Passage(book="GEN", chapter=1, verse_start=1, verse_end=25)
        passage_id = self.db.upsert_passage(passage)

        result = PerspectiveResult(
            perspective="historian",
            status=PerspectiveStatus.COMPLETED,
            content="Analysis content here",
            input_tokens=100,
            output_tokens=500,
            duration_ms=2000,
        )

        run_id = self.db.save_perspective_run(passage_id, result)
        assert run_id > 0

        runs = self.db.get_perspective_runs(passage_id)
        assert len(runs) == 1
        assert runs[0].perspective == "historian"
        assert runs[0].input_tokens == 100
        assert runs[0].output_tokens == 500

    def test_get_status_summary(self):
        """Test getting status summary."""
        passages = [
            Passage(book="GEN", chapter=1, verse_start=1, verse_end=25, status=PassageStatus.PENDING),
            Passage(book="GEN", chapter=2, verse_start=1, verse_end=3, status=PassageStatus.COMPLETED),
            Passage(book="GEN", chapter=3, verse_start=1, verse_end=7, status=PassageStatus.COMPLETED),
            Passage(book="GEN", chapter=4, verse_start=1, verse_end=16, status=PassageStatus.FAILED),
        ]
        for p in passages:
            self.db.upsert_passage(p)

        summary = self.db.get_status_summary()
        assert summary.pending == 1
        assert summary.completed == 2
        assert summary.failed == 1
        assert summary.total == 4
