import unittest
from unittest.mock import patch

import src.db_helper as db_helper


class DbHelperTests(unittest.TestCase):
    def setUp(self):
        self.app_context = db_helper.app.app_context()
        self.app_context.push()
        self.addCleanup(self.app_context.pop)


class SetupDbTests(DbHelperTests):
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
        mock_inspect.return_value.has_table.assert_called_once_with("sources")
        mock_execute.assert_called_once()
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
            "id INTEGER PRIMARY KEY, name TEXT NOT NULL, pages TEXT)"
        )
        mock_open.return_value.__enter__.return_value.read.return_value = schema
        inspector = mock_inspect.return_value
        inspector.has_table.return_value = True
        inspector.get_columns.return_value = [
            {"name": "id"},
            {"name": "name"},
        ]

        db_helper.setup_db()

        mock_inspect.assert_called_once()
        inspector.get_columns.assert_called_once_with("sources")
        mock_execute.assert_called_once()
        self.assertIn(
            "ALTER TABLE sources ADD COLUMN pages TEXT",
            str(mock_execute.call_args.args[0]),
        )
        mock_commit.assert_called_once_with()

    @patch("builtins.open", create=True)
    @patch("src.db_helper.db.session.commit")
    @patch("src.db_helper.db.session.execute")
    @patch("src.db_helper.inspect")
    def test_commits_without_altering_when_all_columns_exist(
        self, mock_inspect, mock_execute, mock_commit, mock_open
    ):
        schema = "CREATE TABLE sources (id INTEGER PRIMARY KEY, name TEXT)"
        mock_open.return_value.__enter__.return_value.read.return_value = schema
        inspector = mock_inspect.return_value
        inspector.has_table.return_value = True
        inspector.get_columns.return_value = [{"name": "id"}, {"name": "name"}]

        db_helper.setup_db()

        mock_execute.assert_not_called()
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
            "id INTEGER PRIMARY KEY, name TEXT, required_value TEXT NOT NULL)"
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

    @patch("builtins.open", create=True)
    @patch("src.db_helper.db.session.commit")
    @patch("src.db_helper.db.session.execute")
    @patch("src.db_helper.inspect")
    def test_rejects_missing_primary_key_column(
        self, mock_inspect, mock_execute, mock_commit, mock_open
    ):
        schema = "CREATE TABLE sources (id INTEGER PRIMARY KEY, name TEXT)"
        mock_open.return_value.__enter__.return_value.read.return_value = schema
        inspector = mock_inspect.return_value
        inspector.has_table.return_value = True
        inspector.get_columns.return_value = [{"name": "name"}]

        with self.assertRaisesRegex(
            ValueError, "Cannot automatically add required or primary-key columns"
        ):
            db_helper.setup_db()

        mock_execute.assert_not_called()
        mock_commit.assert_not_called()


class SourceQueryTests(DbHelperTests):
    @patch("src.db_helper.db.session.execute")
    def test_get_source_returns_first_mapping(self, mock_execute):
        expected = {
            "id": 7,
            "name": "A title",
            "type": "book",
            "author": "A. Author",
            "publish_year": 2024,
            "pages": "12-20",
        }
        mock_execute.return_value.mappings.return_value.first.return_value = expected

        result = db_helper.get_source(7)

        self.assertIs(result, expected)
        self.assertIn("SELECT *", str(mock_execute.call_args.args[0]))
        self.assertIn(":source_id", str(mock_execute.call_args.args[0]))
        self.assertEqual(mock_execute.call_args.args[1], {"source_id": 7})

    @patch("src.db_helper.db.session.execute")
    def test_get_source_returns_none_when_no_row_exists(self, mock_execute):
        mock_execute.return_value.mappings.return_value.first.return_value = None

        result = db_helper.get_source(999)

        self.assertIsNone(result)
        self.assertEqual(mock_execute.call_args.args[1], {"source_id": 999})

    @patch("src.db_helper.db.session.commit")
    @patch("src.db_helper.db.session.execute")
    def test_add_source_inserts_provided_values_and_commits(
        self, mock_execute, mock_commit
    ):
        values = {
            "name": "A title",
            "type": "book",
            "author": "A. Author",
            "publish_year": 2024,
            "pages": "12-20",
        }

        db_helper.add_source(values)

        sql = str(mock_execute.call_args.args[0])
        self.assertIn("INSERT INTO sources", sql)
        self.assertIn("name, type, author, publish_year, pages", sql)
        self.assertIn(":name, :type, :author, :publish_year, :pages", sql)
        self.assertEqual(mock_execute.call_args.args[1], values)
        mock_commit.assert_called_once_with()

    @patch("src.db_helper.db.session.execute")
    def test_get_all_sources_returns_rows_and_selects_expected_fields(self, mock_execute):
        rows = [(1, "First", "book", "Author One", 2020, "1-10")]
        mock_execute.return_value.fetchall.return_value = rows

        result = db_helper.get_all_sources()

        self.assertIs(result, rows)
        sql = str(mock_execute.call_args.args[0])
        self.assertIn("id, name, type, author, publish_year, pages", sql)
        self.assertIn("ORDER BY id ASC", sql)
        mock_execute.assert_called_once()

    @patch("src.db_helper.db.session.commit")
    @patch("src.db_helper.db.session.execute")
    def test_update_source_updates_whitelisted_fields_and_commits(
        self, mock_execute, mock_commit
    ):
        db_helper.update_source(7, {
            "name": "Updated title",
            "author": "Updated author",
            "unexpected": "ignored",
        })

        sql = str(mock_execute.call_args.args[0])
        self.assertIn("UPDATE sources SET", sql)
        self.assertIn("name = :name", sql)
        self.assertIn("author = :author", sql)
        self.assertNotIn("unexpected", sql)
        parameters = mock_execute.call_args.args[1]
        self.assertEqual(parameters["source_id"], 7)
        self.assertEqual(parameters["name"], "Updated title")
        mock_commit.assert_called_once_with()

    @patch("src.db_helper.db.session.commit")
    @patch("src.db_helper.db.session.execute")
    def test_hide_source_soft_deletes_instead_of_removing_row(
        self, mock_execute, mock_commit
    ):
        db_helper.hide_source(7)

        sql = str(mock_execute.call_args.args[0])
        self.assertIn("SET hidden = 1", sql)
        self.assertIn("WHERE id = :source_id", sql)
        self.assertEqual(mock_execute.call_args.args[1], {"source_id": 7})
        mock_commit.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
