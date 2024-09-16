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

# This is an example of a MySQL Table
class User(ModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    primary_email = db.Column(db.String(254), unique=True, nullable=False)
    secondary_email = db.Column(db.String(254), unique=False, nullable=True)