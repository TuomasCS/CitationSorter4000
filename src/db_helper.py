from config import db, app
from sqlalchemy import text
import os

with app.app_context():
   db.session.execute(text("DROP TABLE IF EXISTS sources"))

   schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

   with open(schema_path, 'r') as f:
      schema_sql = f.read().strip()
   
   sql = text(schema_sql)
   db.session.execute(sql)
   db.session.commit()