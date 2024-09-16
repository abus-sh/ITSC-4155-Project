from flask import Blueprint
from utils.queries import *

homepage = Blueprint('homepage', __name__)


@homepage.route('/')
def home():
    return "<p>Hello world!</p>"

# This is an example
@homepage.route('/test')
def example_of_query():
    add_user('Alberto Olivi', 'alberto@gmail.com', None)
    user = get_user_by_email('alberto@gmail.com', dict=True)
    return user
    # {"id":1,"name":"Alberto Olivi","primary_email":"alberto@gmail.com","secondary_email":null}