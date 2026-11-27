from src.config import db, app
from sqlalchemy import text
import os


def tables():
  """Returns all table names from the database"""
  sql = text(
    "SELECT name FROM sqlite_master "
    "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
  )

  result = db.session.execute(sql)
  return [row[0] for row in result.fetchall()]

def setup_db():
  """
    Creating the database
    If database tables already exist, those are dropped before the creation
  """
  tables_in_db = tables()
  if len(tables_in_db) > 0:
    print(f"Tables exist, dropping: {', '.join(tables_in_db)}")
    for table in tables_in_db:
      sql = text(f"DROP TABLE {table}")
      db.session.execute(sql)
    db.session.commit()

  print("Creating database")
  
  # Read schema from schema.sql file
  schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
  with open(schema_path, 'r') as f:
    schema_sql = f.read().strip()
  
  sql = text(schema_sql)
  db.session.execute(sql)
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
   sql = """SELECT *
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