from flask import Blueprint

auth = Blueprint('authentication', __name__)


@auth.route('/')
def authentication():
    return "<p>Authentication</p>"