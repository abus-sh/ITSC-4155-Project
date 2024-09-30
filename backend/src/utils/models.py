from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.inspection import inspect
import string, random


# Initialize SQLAlchemy
db = SQLAlchemy()

# Class Model to return queries as dict
class ModelMixin:
    def to_dict(self):
        """Automatically converts all columns of the model to a dictionary."""
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


def gen_unique_login_id(length=8, max_attempts=3):
    """Generate a unique login_id for a new User using UPPERCASE letters and 0-9 digits."""
    attempts = 0
    characters = string.ascii_uppercase + string.digits
    while attempts < max_attempts:
        login_id = ''.join(random.choice(characters) for _ in range(length))
        if not User.query.filter_by(login_id=login_id).first():
            return login_id
        attempts += 1
    raise Exception("Failed to generate a unique login_id after maximum attempts.")


#######################################################################
#                                                                     #
#                          DATABASE TABLES                            #
#                                                                     #
#######################################################################

# The user table
class User(UserMixin, ModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=False, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)
    canvas_token_password = db.Column(db.String(200), unique=False, nullable=False)
    canvas_token_password = db.Column(db.String(200), unique=False, nullable=False)

    # Tokens encrypted with session key
    canvas_token_session = None         # Placeholder for encrypted token with session key
    todoist_token_session = None        # Placeholder for encrypted token with session key

    # When the `login_manager.user_loader` is run for the login, this is the parameter it will use 
    def get_id(self):
        return str(self.login_id)
    
    def set_encrypted_session_tokens(self, canvas_token_session, todoist_token_session):
        self.canvas_token_session = canvas_token_session
        self.todoist_token_session = todoist_token_session
