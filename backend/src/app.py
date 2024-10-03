from flask import Flask
from flask_cors import CORS
import os

from api.v1.task import api_v1
from endpoints.authentication import auth, login_manager, csrf
from endpoints.homepage import homepage
from utils.models import db


app = Flask(__name__)
USING_SQLITE = False


app.register_blueprint(homepage, url_prefix='/')        # Homepage Endpoint
app.register_blueprint(auth, url_prefix='/api/auth')    # Authentication Endpoint
app.register_blueprint(api_v1, url_prefix='/api/v1')    # API V1 Endpoint


# Read the connection string from a file or environment variable
# Example of string: 'mysql+pymysql://username:password@localhost:3306/db_name'
with open(os.environ.get('DB_CONN_FILE', '../../secrets/connection_string.txt'), 'r') as file:
    connection_string = file.readline().strip()

# Read the application secret for signing sessions
# This should be a securely generated random value
with open(os.environ.get('SESSION_SECRET_FILE', '../../secrets/session_secret.txt'), 'r') as file:
    session_secret = file.readline().strip()


# If we decide to not use MySQL then turn `USING_SQLITE`` to True.
# SQLite will create the .db file if it doesn't exist; if it does, it will connect to it (in the /database/ folder).
if USING_SQLITE:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.root_path, "../..", "database", "canvas_hub.db")}'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = session_secret
app.config['WTF_CSRF_FIELD_NAME'] = 'csrf_token'
app.config['WTF_CSRF_SECRET_KEY'] = session_secret
app.config['SESSION_COOKIE_SAMESITE'] = 'None' # Frontend (Angular) and backend (Flask) are on different domains or ports,
app.config['SESSION_COOKIE_SECURE'] = True  # This must be set if using HTTPS


# Initiate database, login manager, and CSRF
db.init_app(app)
login_manager.init_app(app)

# Only enable CSRF protection if not in debug mode
if not app.debug:
    csrf.init_app(app)

# Cross Origin Resource sharing configuration. 
# Only allow request from this address (Angular frontend)
CORS(app, supports_credentials=True, origins=['http://localhost:4200'])


# Create all missing tables based on the table models in `backend/src/utils/models.py`
with app.app_context():
    db.create_all()

# Run Flask with debug for testing purposes
if __name__ == '__main__':
    app.run(debug=True)
