from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect


# Initialize SQLAlchemy
db = SQLAlchemy()

# Class Model to return queries as dict
class ModelMixin:
    def to_dict(self):
        """Automatically converts all columns of the model to a dictionary."""
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}



#######################################################################
#                                                                     #
#                          DATABASE TABLES                            #
#                                                                     #
#######################################################################

# The user table
class User(ModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=False, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)
    canvas_key = db.Column(db.String(120), unique=False, nullable=False)
    todoist_key = db.Column(db.String(90), unique=False, nullable=False)
