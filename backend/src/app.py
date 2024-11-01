from gevent import monkey
monkey.patch_all()

from flask import Flask  # noqa: E402
from flask_cors import CORS  # noqa: E402
import os  # noqa: E402

from api.auth.authentication import auth, login_manager, csrf  # noqa: E402
from api.v1.base import api_v1  # noqa: E402
from utils.models import db  # noqa: E402

app = Flask(__name__)
USING_SQLITE = 'DB_CONN_FILE' not in os.environ


app.register_blueprint(auth, url_prefix='/api/auth')    # Authentication Endpoint
app.register_blueprint(api_v1, url_prefix='/api/v1')    # API V1 Endpoint


# Read the connection string from a file or environment variable
if not USING_SQLITE:
    with open(os.environ.get('DB_CONN_FILE', '../../secrets/connection_string.txt'), 'r') as file:
        connection_string = file.readline().strip()
else:
    connection_string = f'sqlite:///{os.path.join(app.root_path, "../..", "database", "canvas_hub.db")}'  # noqa: E501


# Read the application secret for signing sessions
try:
    with open(os.environ.get('SESSION_SECRET_FILE', '../../secrets/session_secret.txt'), 'r') as file:
        session_secret = file.readline().strip()
except FileNotFoundError:
    # THIS IS ONLY FOR TESTING PURPOSES, IT WILL NOT BE HARCODED IN DEPLOYMENT
    session_secret = "f4wm#*mi83he792#f*&*rsfE$FCS!@G%$RED"


# SQLite will create the .db file if it doesn't exist; if it does, it will connect to it (in the
# /database/ folder).
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = session_secret
app.config['WTF_CSRF_FIELD_NAME'] = 'csrf_token'
app.config['WTF_CSRF_SECRET_KEY'] = session_secret
# Frontend (Angular) and backend (Flask) are on different domains or ports,
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
# This must be set if using HTTPS
app.config['SESSION_COOKIE_SECURE'] = True


# Initiate database, login manager, and CSRF
db.init_app(app)
login_manager.init_app(app)

# Only enable CSRF protection if not in debug mode
if not app.debug and os.environ.get('CSRF', 'ON') == 'ON':
    csrf.init_app(app)

# Cross Origin Resource sharing configuration.
# Only allow request from this address (Angular frontend)
CORS(app, supports_credentials=True, origins=[
    'http://localhost:4200',
    'https://localhost:4200',
    'https://itsc4155.abus.sh:4200'
])


# Create all missing tables based on the table models in `backend/src/utils/models.py`
with app.app_context():
    db.create_all()

# Run Flask with debug for testing purposes
if __name__ == '__main__':
    app.run(debug=True)
