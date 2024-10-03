from argon2.exceptions import VerifyMismatchError
from flask import Blueprint, request, abort, Request, jsonify, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from http import HTTPStatus
from lru import LRU

from utils.queries import get_user_by_username, get_user_by_login_id, add_user, User, password_hasher
from utils.crypto import reencrypt_str, decrypt_str

auth = Blueprint('authentication', __name__)

login_manager = LoginManager()
csrf = CSRFProtect()

# This value effectively limits the maximum number of concurrent sessions
api_key_cache = LRU(50)

# Retrieve the User based on the login_id stored in the session
@login_manager.user_loader
def user_loader(login_id):
    db_user: User | None = get_user_by_login_id(login_id)

    if db_user == None:
        return None
    
    # Try to get the re-encrypted API keys
    # If they don't exist, invalidate the session
    if session['_id'] not in api_key_cache:
        return None

    # Load cached values for the API tokens
    canvas_key, todoist_key = api_key_cache[session['_id']]
    db_user.canvas_token_session = canvas_key
    db_user.todoist_token_session = todoist_key
    db_user.todoist_token_session = todoist_key

    return db_user

#################################################################
#                                                               #
#                     LOGIN, SIGNUP, LOGOUT                     #
#                                                               #
#################################################################

@auth.route('/login', methods=['POST'])
def login():

    # User is already logged in
    if current_user.is_authenticated:
        abort(HTTPStatus.UNAUTHORIZED)
        return
    
    parameters = get_authentication_params(request, include_tokens=False)
    
    # Ensure the parameters were succesfully extracted from the body of the request
    if parameters is None:
        abort(HTTPStatus.BAD_REQUEST)
        return
    
    username, password = parameters

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

    # Update the session for the user using the User's login_id 
    login_user(db_user)

    # Get the session identifier from the session
    # This is provided by Flask-Login as a unique identifer
    session_id = session['_id']

    # Decrypt tokens with password and re-encrypt with session_id
    canvas_token = reencrypt_str(db_user.canvas_token_password, password, session_id)
    todoist_token = reencrypt_str(db_user.todoist_token_password, password, session_id)

    # Cache API re-encrypted tokens for future requests
    api_key_cache[session_id] = (canvas_token, todoist_token)

    # Respond that the user was authenticated
    return jsonify({'success': True, 'message': f"Logged in as {db_user.username}"})


@auth.route('/signup', methods=['POST'])
def sign_up():

    parameters = get_authentication_params(request, include_tokens=True)
    
    # Ensure the parameters were succesfully extracted from the body of the request
    if parameters is None:
        abort(HTTPStatus.BAD_REQUEST)
        return
    
    username, password, canvasToken, todoistToken = parameters
    

    # If the username is invalid, determine it to be unprocessable
    # This is so that it is distinct from a bad request
    if not _is_valid_username(username):
        abort(HTTPStatus.BAD_REQUEST)
        return

    # If the password is invalid, determine it to be unprocessable
    # This is so that it is distinct from a bad request
    if not _is_valid_password(password):
        abort(HTTPStatus.BAD_REQUEST)
        return


    # Create the user, tokens are encrypted and password is hashed
    if not add_user(username, password, canvasToken, todoistToken):
        abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        return
    
    # Respond that the user was created
    return jsonify({'success': True, 'message': f"Account created for {username}"})

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
def get_csrf_token():
    token = generate_csrf()
    return jsonify({'csrf_token': token})

@auth.route('/status', methods=['GET'])
def auth_status():
    if current_user.is_authenticated:
        return jsonify({'authenticated': True, 'user': {'id': current_user.id, 'username': current_user.username}}), 200
    return jsonify({'authenticated': False}), 200


#################################################################
#                                                               #
#                 Authentication Utilities                      #
#                                                               #
#################################################################

def get_authentication_params(request: Request, include_tokens: bool=False) -> tuple[str, str] | tuple[str, str, str, str] |None:
    """
    Extracts the username and password from a request, if both exist and are valid.

    :param request: The Flask request to validate.
    :param include_tokens: If to extract the tokens from the request, will return a tuple[str, str, str, str].
    :return tuple[str, str]: Returns the username and password if both exist and are valid. `include_tokens` is False.
    :return tuple[str, str, str, str]: Returns the username, password, and the tokens if they all exist and are valid.
    :return None: Returns None if the username, password or the tokens don't exist or are invalid.
    """
    # There is no json data in the request
    if not request.json:
        return None

    # If the request json can't be parsed, return None
    username = request.json.get('username')
    password = request.json.get('password')

    if include_tokens:
        canvas_token = request.json.get('canvas_token')
        todoist_token = request.json.get('todoist_token')
        params = (username, password, canvas_token, todoist_token)
    else:
        params = (username, password)

    # Check that all fields of params are string and not None
    if any(param is None or not isinstance(param, str) for param in params):
        return None

    return params

def _is_valid_username(username: str) -> bool:
    """
    Determines if a given username complies with the username requirements for the site.

    :param username: The username to validate.
    :return bool: True if the username complies with the requirements, False otherwise.
    """

    # If the username is empty or too long, return False
    username_len = len(username)
    if username_len == 0 or username_len > 90:
        return False
    
    # If the username includes a newline, return False
    if username.count('\n') != 0:
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

def decrypt_api_keys() -> tuple[str, str]:
    """
    Decrypts the API keys for the current user. Returns them as (canvas_key, todoist_key).

    :rasies ValueError: If session does not have an _id or current_user has no encrypted API keys.
    """
    # If the session doesn't have an ID, can't decrypt keys
    if '_id' not in session:
        raise ValueError
    session_id = session['_id']

    # If current user doesn't have API keys encrypted w/ session key, can't decrypt keys
    if current_user.canvas_token_session == None or current_user.todoist_token_session == None:
        raise ValueError

    canvas_token = decrypt_str(current_user.canvas_token_session, session_id)
    todoist_token = decrypt_str(current_user.todoist_token_session, session_id)

    return (canvas_token, todoist_token)
