from flask import Blueprint, request, abort, Request, jsonify
from http import HTTPStatus
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from utils.queries import get_user_by_username, add_user, User
import flask_login
import utils.crypto as crypto
import base64
from lru import LRU

auth = Blueprint('authentication', __name__)

login_manager = flask_login.LoginManager()
password_hasher = PasswordHasher()
api_key_cache =  LRU(3) # TODO: set to higher value (50?) or swap to redis

class AuthUser(flask_login.UserMixin):
    """
    A respresentation of an authenticated user with an active session.
    """
    def __init__(self, canvas_key: bytes, todoist_key: bytes, session_key: bytes|None=None):
        super().__init__()

        self.canvas_key = canvas_key
        self.todoist_key = todoist_key
        self.session_key = session_key
    

    def decrypt_api_keys(self, session_key: bytes|None=None) -> tuple[str, str]:
        """
        Decrypts the Canvas and Todoist API keys for the given AuthUser.

        :param session_key: The key to decrypt the API keys. If the AuthUser already has a session
        key, this will be ignored. If one is not specified and the AuthUser doesn't have a session
        key, a ValueError will be raised.
        :return tuple[str, str]: The decrypted Canvas and Todoist API keys.
        :raise ValueError: If no session key is specified and the AuthUser doesn't have one.
        """
        if self.session_key != None:
            session_key = base64.b64decode(self.session_key)
        elif session_key != None:
            session_key = base64.b64decode(self.session_key)
        else:
            raise ValueError

        canvas_key = crypto.decrypt_str(self.canvas_key, session_key)
        todoist_key = crypto.decrypt_str(self.todoist_key, session_key)

        return (canvas_key, todoist_key)


# Convert a username to an AuthUser, returns None if no user exists with the specified username
# Automatically called by Flask-Login as needed
@login_manager.user_loader
def user_loader(session_id):
    # Extract the username and session decryption key from the session id
    # If the ID doesn't contain a username and session key, invalidate the session
    if session_id.count('\n') != 1:
        return None
    username, session_key = session_id.split('\n')

    # Check if a user with the username exists, return None if not
    db_user: User|None = get_user_by_username(username)
    if db_user == None:
        return None

    # Try to get the re-encrypted API keys
    # If they don't exist, invalidate the session
    if db_user.username not in api_key_cache:
        return None

    canvas_key, todoist_key = api_key_cache[db_user.username]

    auth_user = AuthUser(canvas_key, todoist_key, session_key=session_key)
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

    # Create a session key to re-encrypt the API keys
    session_key = crypto.generate_key()

    # Re-encrypt the API keys with the session key
    canvas_key = crypto.reencrypt_str(db_user.canvas_key, password, session_key)
    todoist_key = crypto.reencrypt_str(db_user.todoist_key, password, session_key)

    # Cache the re-encrypted API keys so they can be retrieved later
    api_key_cache[db_user.username] = (canvas_key, todoist_key)

    # Base64 encode the session decryption key to store it in the session
    session_key = base64.b64encode(session_key).decode()

    # Create a session for the user
    # NOTE: the ID used here is different that the ID used in user_loader
    # This uses 'username\nsession_key', while user_load uses just 'username' as the ID
    # If any strange bugs occur with auth, they probably are from here
    auth_user = AuthUser(canvas_key, todoist_key)
    auth_user.id = db_user.username + '\n' + session_key
    flask_login.login_user(auth_user)

    # Respond that the user was authenticated
    response = dict()
    response['username'] = db_user.username
    return jsonify(response)


@auth.route('/signup', methods=['POST'])
def sign_up():
    username, password = _get_authentication_params(request)
    canvas_key, todoist_key = _get_api_keys(request)

    # Ensure the provided username and password are valid
    if username == None or password == None:
        abort(HTTPStatus.BAD_REQUEST)
        return

    # Ensure that the provided API keys are valid
    if canvas_key == None or todoist_key == None:
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

    # Encrypt the API tokens
    canvas_key = crypto.encrypt_str(canvas_key, password)
    todoist_key = crypto.encrypt_str(todoist_key, password)

    # Create the user
    # TODO: determine if sign up failure was because of duplicate username or some other reason
    if not add_user(username, pw_hash, bytes(canvas_key), bytes(todoist_key)):
        abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        return

    # Respond that the user was created
    response = dict()
    response['username'] = username
    return jsonify(response)


@auth.route('/protected')
@flask_login.login_required
def protected():
    print(flask_login.current_user.id)
    print(flask_login.current_user.session_key)

    canvas_key, todoist_key = flask_login.current_user.decrypt_api_keys()
    print(canvas_key)
    print(todoist_key)

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


def _get_api_keys(request: Request) -> tuple[str, str] | tuple[None, None]:
    """
    Extracts the Canvas API key and Todoist API key from a request, if both exist and are valid.

    :param request: The Flask request to validate.
    :return tuple[str, str]: Returns the Canvas and Todoist API key if both exist and are valid.
    :return tuple[None, None]: Returns (None, None) if the API keys don't exist or are invalid.
    """
    canvas_key = request.json.get('canvas_key')
    todoist_key = request.json.get('todoist_key')

    # Make sure the API keys were supplied
    if canvas_key == None or todoist_key == None:
        return (None, None)
    
    # Make sure they are strings
    if type(canvas_key) != str or type(todoist_key) != str:
        return (None, None)
    
    # Make sure they are non-empty
    if len(canvas_key) == 0 or len(todoist_key) == 0:
        return (None, None)

    return (canvas_key, todoist_key)


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