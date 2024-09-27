from endpoints.authentication import auth
from endpoints.homepage import homepage
from utils.models import db
from api.v1.task import api_v1
from flask import Flask


app = Flask(__name__)

app.register_blueprint(homepage, url_prefix='/')        # Homepage Endpoint
app.register_blueprint(auth, url_prefix='/auth')        # Authentication Endpoint

app.register_blueprint(api_v1, url_prefix='/api/v1')    # API V1 Endpoint


# Read the connection string from a file or environment variable
# Example of string: 'mysql+pymysql://username:password@localhost:3306/db_name'
with open('../../secrets/connection_string.txt', 'r') as file:
    connection_string = file.readline().strip()

app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database with App
db.init_app(app)

# Create all missing tables based on the table models in `backend/src/utils/models.py`
with app.app_context():
    db.create_all()

# Run Flask with debug for testing purposes
app.run(debug=True)