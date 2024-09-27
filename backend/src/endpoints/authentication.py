from flask import Blueprint, request, abort, Request, jsonify
from flask_login import LoginManager, UserMixin, login_required, login_user
from http import HTTPStatus
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from utils.queries import get_user_by_username, add_user, User

auth = Blueprint('authentication', __name__)

login_manager = LoginManager()
password_hasher = PasswordHasher()

class AuthUser(UserMixin):
    """
    A respresentation of an authenticated user with an active session.
    """
    pass


# Convert a username to an AuthUser, returns None if no user exists with the specified username
# Automatically called by Flask-Login as needed
@login_manager.user_loader
def user_loader(username):
    # Check if a user with the username exists, return None if not
    db_user: User|None = get_user_by_username(username)
    if db_user == None:
        return None
    
    auth_user = AuthUser()
    auth_user.id = db_user.username
    return auth_user


@auth.route('/login', methods=['POST'])
def login():
    username, password = _get_authentication_params(request)

    # Ensure the provided username and password are valid
    if username == None or password == None:
        abort(HTTPStatus.BAD_REQUEST)
        return

    db_user: User|None = get_user_by_username(username)
    
    # If no user exists, consider the request unauthorized
    if db_user == None:
        abort(HTTPStatus.UNAUTHORIZED)
        return
    
    # If the password is incorrect, consider the request unauthorized
    # Do not disintguish between no such user and an invalid password
    try:
        password_hasher.verify(db_user.password, password)
    except VerifyMismatchError:
        abort(HTTPStatus.UNAUTHORIZED)
        return

    # Create a session for the user
    auth_user = AuthUser()
    auth_user.id = db_user.username
    login_user(auth_user)

    # Respond that the user was authenticated
    response = dict()
    response['username'] = auth_user.id
    return jsonify(response)

@auth.route('/signup', methods=['POST'])
def sign_up():
    username, password = _get_authentication_params(request)

    # Ensure the provided username and password are valid
    if username == None or password == None:
        abort(HTTPStatus.BAD_REQUEST)
        return

    # Validate the username, determine it to be unprocessable if it isn't valid
    if not _is_valid_username(username):
        abort(HTTPStatus.BAD_REQUEST)
        return

    # If the password is invalid, determine it to be unprocessable
    # This is so that it is distinct from a bad request
    if not _is_valid_password(password):
        abort(HTTPStatus.BAD_REQUEST)
        return

    # Hash the password
    pw_hash = password_hasher.hash(password)

    # Create the user
    # TODO: determine if sign up failure was because of duplicate username or some other reason
    if not add_user(username, pw_hash):
        abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        return

    # Respond that the user was created
    response = dict()
    response['username'] = username
    return jsonify(response)

@auth.route('/protected')
@login_required
def protected():
    return "Hi"


def _get_authentication_params(request: Request) -> tuple[str, str] | tuple[None, None]:
    """
    Extracts the username and password from a request, if both exist and are valid.

    :param request: The Flask request to validate.
    :return tuple[str, str]: Returns the username and password if both exist and are valid.
    :return tuple[None, None]: Returns (None, None) if the username and password don't exist or are
    invalid.
    """
    username = request.json.get('username')
    password = request.json.get('password')

    # Make sure a username and password were supplied
    if username == None or password == None:
        return (None, None)

    # Make sure the username and password are strings
    if type(username) != str or type(password) != str:
        return (None, None)

    return (username, password)


def _is_valid_username(username: str) -> bool:
    """
    Determines if a given username complies with the username requirements for the site.

    :param username: The username to validate.
    :return bool: True if the username complies with the requirements, False otherwise.
    """

    # If the username is empty or too long, return false
    username_len = len(username)
    if username_len == 0 or username_len > 90:
        return False
    
    return True

def _is_valid_password(password: str) -> bool:
    """
    Determines if a given password complies with the password requirements for the site. The
    password requirements are taken from NIST SP800-63B section 3.1.1.2.
    https://pages.nist.gov/800-63-4/sp800-63b.html#passwordver

    :param password: The password to validate.
    :return bool: True if the password complies with the requirements, False otherwise.
    """

    # Minimum of 15 characters
    if len(password) < 15:
        return False

    # Password maximum of 128 characters, double the minimum of 64
    if len(password) > 128:
        return False
    
    # NIST SP800-63B explicitly prohibits requiring special characters and other complexity rules

    return True