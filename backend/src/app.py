from flask import Flask
from sqlalchemy import create_engine, text
import os
import sys

app = Flask(__name__)
engine = None

@app.route("/")
def hello_world():
    with engine.connect() as connection:
        # Will replace this with a proper ORM setup, this is just for testing
        result = connection.execute(text("SELECT 1"))
        num = result.first()[0]

    return f"<p>{num} was selected</p>"

with app.app_context():
    db_conn_file = os.environ.get("DB_CONN_FILE", "../../secrets/database_conn_dev.txt")
    if not os.path.exists(db_conn_file):
        print("Fatal error: database connection file doesn't exist")
        sys.exit(-1)
    with open(db_conn_file) as f:
        engine = create_engine(f.read().strip())
    try:
        # Ensure the provided string is valid
        db_conn = engine.connect()
    except Exception as e:
        print("Fatal error: unable to connect to database")
        print(e)

if __name__ == '__main__':
    app.run()
