from config import db, app
from sqlalchemy import inspect, text
import os


def ensure_url_column():
   columns = inspect(db.engine).get_columns("sources")
   if not any(column["name"] == "url" for column in columns):
      db.session.execute(text("ALTER TABLE sources ADD COLUMN url TEXT"))
      db.session.commit()


def setup_db():
   db.session.execute(text("DROP TABLE IF EXISTS sources"))

   schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

   with open(schema_path, 'r') as f:
      schema_sql = f.read().strip()
      
   sql = text(schema_sql)
   db.session.execute(sql)
   db.session.commit()

def get_source(source_id):
   ensure_url_column()
   sql = """SELECT name, type, author, publish_year, url
            FROM sources
            WHERE id = :source_id"""
   result = db.session.execute(text(sql), {"source_id":source_id}).fetchall()
   return result[0] if result else None


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