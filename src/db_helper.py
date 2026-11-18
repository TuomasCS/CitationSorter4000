from src.config import db, app
from sqlalchemy import inspect, text
import os
import sqlite3
from contextlib import closing


def ensure_url_column():
   columns = inspect(db.engine).get_columns("sources")
   if not any(column["name"] == "url" for column in columns):
      db.session.execute(text("ALTER TABLE sources ADD COLUMN url TEXT"))
      db.session.commit()


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
   ensure_url_column()
   sql = """SELECT name, type, author, publish_year, url
            FROM sources
            WHERE id = :source_id"""
   result = db.session.execute(text(sql), {"source_id":source_id})
   return result.mappings().first() if result else None


def add_source(name, source_type, author, publish_year, url):
   ensure_url_column()
   sql = """INSERT INTO sources (name, type, author, publish_year, url)
            VALUES (:name, :type, :author, :publish_year, :url)"""
   db.session.execute(
      text(sql),
      {
         "name": name,
         "type": source_type,
         "author": author,
         "publish_year": publish_year,
         "url": url,
      },
   )
   db.session.commit()


def get_all_sources():
   sql = """SELECT id, name
            FROM sources
            ORDER BY id ASC"""
   return db.session.execute(text(sql)).fetchall()

if __name__ == "__main__":
   with app.app_context():
      setup_db()