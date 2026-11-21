import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

# Ensure the project root (the directory containing src/) is importable even
# when pytest is launched with a different working directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.db_helper as db_helper


class EnsureUrlColumnTests(unittest.TestCase):
    def setUp(self):
        self.app_context = db_helper.app.app_context()
        self.app_context.push()
        self.addCleanup(self.app_context.pop)

    @patch("src.db_helper.db.session.commit")
    @patch("src.db_helper.db.session.execute")
    @patch("src.db_helper.inspect")
    def test_adds_url_column_when_missing(self, mock_inspect, mock_execute, mock_commit):
        mock_inspect.return_value.get_columns.return_value = [
            {"name": "id"},
            {"name": "name"},
        ]

        db_helper.ensure_url_column()

        self.assertEqual(mock_execute.call_count, 1)
        self.assertIn("ALTER TABLE sources ADD COLUMN url TEXT", str(mock_execute.call_args.args[0]))
        mock_commit.assert_called_once_with()

    @patch("src.db_helper.db.session.commit")
    @patch("src.db_helper.db.session.execute")
    @patch("src.db_helper.inspect")
    def test_does_not_change_table_when_url_exists(self, mock_inspect, mock_execute, mock_commit):
        mock_inspect.return_value.get_columns.return_value = [
            {"name": "id"},
            {"name": "url"},
        ]

        db_helper.ensure_url_column()

        mock_execute.assert_not_called()
        mock_commit.assert_not_called()


class SetupDbTests(unittest.TestCase):
    def setUp(self):
        self.app_context = db_helper.app.app_context()
        self.app_context.push()
        self.addCleanup(self.app_context.pop)

    @patch("builtins.open", create=True)
    @patch("src.db_helper.db.session.commit")
    @patch("src.db_helper.db.session.execute")
    @patch("src.db_helper.inspect")
    def test_creates_table_when_it_does_not_exist(
        self, mock_inspect, mock_execute, mock_commit, mock_open
    ):
        schema = "CREATE TABLE sources (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
        mock_open.return_value.__enter__.return_value.read.return_value = schema
        mock_inspect.return_value.has_table.return_value = False

        db_helper.setup_db()

        mock_open.assert_called_once()
        self.assertEqual(mock_execute.call_count, 1)
        self.assertEqual(str(mock_execute.call_args.args[0]), schema)
        mock_commit.assert_called_once_with()

    @patch("builtins.open", create=True)
    @patch("src.db_helper.db.session.commit")
    @patch("src.db_helper.db.session.execute")
    @patch("src.db_helper.inspect")
    def test_adds_missing_nullable_column_to_existing_table(
        self, mock_inspect, mock_execute, mock_commit, mock_open
    ):
        schema = (
            "CREATE TABLE sources ("
            "id INTEGER PRIMARY KEY, name TEXT NOT NULL, url TEXT)"
        )
        mock_open.return_value.__enter__.return_value.read.return_value = schema
        inspector = mock_inspect.return_value
        inspector.has_table.return_value = True
        inspector.get_columns.return_value = [
            {"name": "id"},
            {"name": "name"},
        ]

        db_helper.setup_db()

        self.assertEqual(mock_execute.call_count, 1)
        self.assertIn("ALTER TABLE sources ADD COLUMN url TEXT", str(mock_execute.call_args.args[0]))
        mock_commit.assert_called_once_with()

    @patch("builtins.open", create=True)
    @patch("src.db_helper.db.session.commit")
    @patch("src.db_helper.db.session.execute")
    @patch("src.db_helper.inspect")
    def test_rejects_missing_required_column(
        self, mock_inspect, mock_execute, mock_commit, mock_open
    ):
        schema = (
            "CREATE TABLE sources ("
            "id INTEGER PRIMARY KEY, name TEXT NOT NULL, required_value TEXT NOT NULL)"
        )
        mock_open.return_value.__enter__.return_value.read.return_value = schema
        inspector = mock_inspect.return_value
        inspector.has_table.return_value = True
        inspector.get_columns.return_value = [{"name": "id"}, {"name": "name"}]

        with self.assertRaisesRegex(
            ValueError, "Cannot automatically add required or primary-key columns"
        ):
            db_helper.setup_db()

        mock_execute.assert_not_called()
        mock_commit.assert_not_called()


class SourceQueryTests(unittest.TestCase):
    @patch("src.db_helper.ensure_url_column")
    @patch("src.db_helper.db.session.execute")
    def test_get_source_returns_first_mapping(self, mock_execute, mock_ensure_url):
        expected = {"name": "A title", "type": "book"}
        mock_execute.return_value.mappings.return_value.first.return_value = expected

        result = db_helper.get_source(17)

        self.assertIs(result, expected)
        mock_ensure_url.assert_called_once_with()
        self.assertIn(":source_id", str(mock_execute.call_args.args[0]))
        self.assertEqual(mock_execute.call_args.args[1], {"source_id": 17})

    @patch("src.db_helper.ensure_url_column")
    @patch("src.db_helper.db.session.execute")
    def test_get_source_returns_none_when_no_row_exists(self, mock_execute, _mock_ensure_url):
        mock_execute.return_value.mappings.return_value.first.return_value = None

        self.assertIsNone(db_helper.get_source(999))

    @patch("src.db_helper.db.session.commit")
    @patch("src.db_helper.db.session.execute")
    @patch("src.db_helper.ensure_url_column")
    def test_add_source_inserts_all_values_and_commits(
        self, mock_ensure_url, mock_execute, mock_commit
    ):
        db_helper.add_source("Title", "book", "A. Author", 2024, "https://example.test")

        mock_ensure_url.assert_called_once_with()
        params = mock_execute.call_args.args[1]
        self.assertEqual(
            params,
            {
                "name": "Title",
                "type": "book",
                "author": "A. Author",
                "publish_year": 2024,
                "url": "https://example.test",
            },
        )
        self.assertIn("INSERT INTO sources", str(mock_execute.call_args.args[0]))
        mock_commit.assert_called_once_with()

    @patch("src.db_helper.db.session.execute")
    def test_get_all_sources_returns_rows_ordered_by_id(self, mock_execute):
        rows = [(1, "First"), (2, "Second")]
        mock_execute.return_value.fetchall.return_value = rows

        result = db_helper.get_all_sources()

        self.assertIs(result, rows)
        self.assertIn("ORDER BY id ASC", str(mock_execute.call_args.args[0]))
        self.assertEqual(mock_execute.call_count, 1)


if __name__ == "__main__":
    unittest.main()
