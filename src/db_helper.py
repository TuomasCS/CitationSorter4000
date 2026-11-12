from config import db, app
from sqlalchemy import text
import os

def setup_db():
   db.session.execute(text("DROP TABLE IF EXISTS sources"))

   schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

   with open(schema_path, 'r') as f:
      schema_sql = f.read().strip()
      
   sql = text(schema_sql)
   db.session.execute(sql)
   db.session.commit()

def get_source(source_id):
   sql = """SELECT name, type, author, publish_year
            FROM sources
            WHERE id = :source_id"""
   result = db.session.execute(text(sql), {"source_id":source_id}).fetchall()
   return result[0] if result else None


def get_all_sources():
   sql = """SELECT id, name
            FROM sources
            ORDER BY id ASC"""
   return db.session.execute(text(sql)).fetchall()

if __name__ == "__main__":
   with app.app_context():
      setup_db()