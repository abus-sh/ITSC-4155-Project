from flask import Blueprint, request, abort, Request, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf 
from http import HTTPStatus
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from utils.queries import get_user_by_username, get_user_by_login_id, add_user, User

auth = Blueprint('authentication', __name__)

login_manager = LoginManager()
password_hasher = PasswordHasher()
csrf = CSRFProtect()


# Retrieve the User based on the login_id stored in the session
@login_manager.user_loader
def user_loader(login_id):
    db_user: User | None = get_user_by_login_id(login_id)
    return db_user


#################################################################
#                                                               #
#                     LOGIN, SIGNUP, LOGOUT                     #
#                                                               #
#################################################################

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

    # Create a session for the user using the User's login_id 
    login_user(db_user)

    # Respond that the user was authenticated
    response = dict()
    response['username'] = db_user.username
    return jsonify(response)

@auth.route('/signup', methods=['POST'])
def sign_up():
    username, password = _get_authentication_params(request)

    # Ensure the provided username and password are valid
    if username == None or password == None:
        abort(HTTPStatus.BAD_REQUEST)
        return
    
    # If the password is invalid, determine it to be unprocessable
    # This is so that it is distinct from a bad request
    if not _is_valid_password(password):
        abort(HTTPStatus.UNPROCESSABLE_ENTITY)
        return

    # Hash the password
    pw_hash = password_hasher.hash(password)

    # Create the user
    if not add_user(username, pw_hash):
        abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        return

    # Respond that the user was created
    response = dict()
    response['username'] = username
    return jsonify(response)

@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


#################################################################
#                                                               #
#                 AUTHENTICATION and CSRF TOKEN                 #
#                                                               #
#################################################################

# Get the CSRF Token for the client
@auth.route('/csrf-token', methods=['GET'])
@login_required
def get_csrf_token():
    token = generate_csrf()
    response = jsonify({'csrf_token': token})
    response.set_cookie('XSRF-TOKEN', token)
    return response

@auth.route('/status', methods=['GET'])
def auth_status():
    print(current_user.is_authenticated)
    if current_user.is_authenticated:
        return jsonify({'authenticated': True, 'user': {'id': current_user.id, 'username': current_user.username}}), 200
    return jsonify({'authenticated': False}), 200


@auth.route('/protected')
@login_required
def protected():
    return "Hi"


#################################################################
#                                                               #
#                 Authentication Utilities                      #
#                                                               #
#################################################################

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
    
    # Make sure the username and password are non-empty
    if username == '' or password == '':
        return (None, None)

    return (username, password)


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