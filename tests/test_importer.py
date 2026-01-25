"""Tests for importer module."""

import tempfile
import os
import pytest

from exegesis_tool.database import Database
from exegesis_tool.importer import import_from_todo, parse_passage_reference
from exegesis_tool.models import PassageStatus


class TestImporter:
    """Tests for import functionality."""

    def setup_method(self):
        """Create temporary database and files."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = Database(self.db_path)

    def teardown_method(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_parse_passage_reference(self):
        """Test parsing passage reference strings."""
        book, chapter, v_start, v_end = parse_passage_reference("GEN 01:26-31")
        assert book == "GEN"
        assert chapter == 1
        assert v_start == 26
        assert v_end == 31

    def test_parse_passage_reference_no_leading_zero(self):
        """Test parsing without leading zero in chapter."""
        book, chapter, v_start, v_end = parse_passage_reference("EXO 3:1-12")
        assert book == "EXO"
        assert chapter == 3
        assert v_start == 1
        assert v_end == 12

    def test_parse_passage_reference_invalid(self):
        """Test parsing invalid reference raises error."""
        with pytest.raises(ValueError):
            parse_passage_reference("invalid")

    def test_import_from_todo(self):
        """Test importing passages from TODO.md format."""
        todo_content = """# Exegesis TODO

## Genesis (GEN)

- [✅] GEN 01:1-25 - Creation of the world
- [ ] GEN 01:26-31 - Creation of humanity
- [🔄] GEN 02:1-3 - The seventh day rest
- [❌] GEN 03:1-7 - The temptation and fall
"""
        todo_path = os.path.join(self.temp_dir, "TODO.md")
        with open(todo_path, "w", encoding="utf-8") as f:
            f.write(todo_content)

        count = import_from_todo(self.db, todo_path)
        assert count == 4

        # Verify statuses
        p1 = self.db.get_passage_by_reference("GEN", 1, 1, 25)
        assert p1 is not None
        assert p1.status == PassageStatus.COMPLETED
        assert p1.description == "Creation of the world"

        p2 = self.db.get_passage_by_reference("GEN", 1, 26, 31)
        assert p2 is not None
        assert p2.status == PassageStatus.PENDING

        p3 = self.db.get_passage_by_reference("GEN", 2, 1, 3)
        assert p3 is not None
        assert p3.status == PassageStatus.IN_PROGRESS

        p4 = self.db.get_passage_by_reference("GEN", 3, 1, 7)
        assert p4 is not None
        assert p4.status == PassageStatus.FAILED

    def test_import_preserves_description(self):
        """Test that import preserves passage descriptions."""
        todo_content = """
- [ ] GEN 22:1-19 - The binding of Isaac
"""
        todo_path = os.path.join(self.temp_dir, "TODO.md")
        with open(todo_path, "w", encoding="utf-8") as f:
            f.write(todo_content)

        import_from_todo(self.db, todo_path)

        p = self.db.get_passage_by_reference("GEN", 22, 1, 19)
        assert p is not None
        assert p.description == "The binding of Isaac"
