from src.config import db, app
from sqlalchemy import inspect, text
import os
import sqlite3
from contextlib import closing


def setup_db():
   """Create the sources table or add missing nullable columns, preserving data."""
   schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
   with open(schema_path, 'r', encoding='utf-8') as f:
      schema_sql = f.read().strip()

   inspector = inspect(db.engine)
   if not inspector.has_table("sources"):
      db.session.execute(text(schema_sql))
   else:
      # Read the expected columns without changing the existing database.
      with closing(sqlite3.connect(":memory:")) as schema_db:
         schema_db.executescript(schema_sql)
         schema_columns = schema_db.execute("PRAGMA table_info(sources)").fetchall()

      existing = {column["name"] for column in inspector.get_columns("sources")}
      missing = [column for column in schema_columns if column[1] not in existing]
      if any(column[3] or column[5] for column in missing):
         raise ValueError("Cannot automatically add required or primary-key columns.")

      quote = db.engine.dialect.identifier_preparer.quote
      for _, column, sql_type, _, _, _ in missing:
         sql = f"ALTER TABLE sources ADD COLUMN {quote(column)} {sql_type}"
         db.session.execute(text(sql))

   db.session.commit()


def get_source(source_id):
   sql = """SELECT *
            FROM sources
            WHERE id = :source_id
              AND COALESCE(hidden, 0) = 0"""
   result = db.session.execute(text(sql), {"source_id":source_id})
   return result.mappings().first() if result else None


def add_source(values):
   sub_sql_1 = ", ".join(values.keys())
   sub_sql_2 = ", ".join([f":{val}" for val in values.keys()])

   sql = f"""INSERT INTO sources ({sub_sql_1})
            VALUES ({sub_sql_2})"""
   
   db.session.execute(text(sql), values)
   db.session.commit()


def get_all_sources():
   sql = """SELECT id, name, type, author, publish_year, pages
            FROM sources
            WHERE COALESCE(hidden, 0) = 0
            ORDER BY id ASC"""
   return db.session.execute(text(sql)).fetchall()


def update_source(source_id, values):
   # The explicit list also protects updates from accepting unknown SQL identifiers.
   allowed_fields = {
      "name", "type", "citation_key", "author", "editor", "organization",
      "school", "publisher", "publish_year", "publication_date", "access_date",
      "howpublished", "journal", "booktitle", "volume", "number", "issue",
      "chapter", "pages", "series", "doi", "isbn", "issn", "url", "keywords",
      "note", "extra_fields"
   }.intersection(values)
   if not allowed_fields:
      return

   assignments = ", ".join(
      f"{field} = :{field}" for field in sorted(allowed_fields)
   )
   sql = f"UPDATE sources SET {assignments} WHERE id = :source_id"
   parameters = dict(values)
   parameters["source_id"] = source_id
   db.session.execute(text(sql), parameters)
   db.session.commit()


def hide_source(source_id):
   sql = """UPDATE sources
            SET hidden = 1
            WHERE id = :source_id"""
   db.session.execute(text(sql), {"source_id": source_id})
   db.session.commit()


def delete_source(source_id):
   hide_source(source_id)

if __name__ == "__main__":
   with app.app_context():
      setup_db()