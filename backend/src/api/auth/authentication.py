from argon2.exceptions import VerifyMismatchError
from flask import Blueprint, request, abort, Request, jsonify, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import CSRFProtect
from api.auth.todoist import todoist, exchange_token
from flask_wtf.csrf import generate_csrf
from http import HTTPStatus
from lru import LRU
from utils.settings import time_it

from utils.queries import get_user_by_username, get_user_by_login_id, add_user, User, password_hasher, update_password
from utils.crypto import reencrypt_str


auth = Blueprint('authentication', __name__)
auth.register_blueprint(todoist, url_prefix='/todoist')


login_manager = LoginManager()
csrf = CSRFProtect()
# This value effectively limits the maximum number of concurrent sessions
api_key_cache = LRU(50)


class TodoistAuthInfo:
    """
    Create a representation of a Todoist authentication attempt, both with OAuth and with a
    permanent API key.

    :param code: The OAuth code paramter. None if a permanent key is being used.
    :param state: The OAuth state paramter. None if a permanent key is being used.
    :param token: The permanent API key. None if OAuth is being used.
    :raises ValueError: If token is None and one of code or state is None.
    """
    def __init__(self, code: str|None=None, state: str|None=None, token: str|None=None):
        # Determine if insufficient information was provided to construct an authenticaiton attempt
        # If no permanent API key was provided and one of the OAuth parameteres wasn't provided,
        # then something is wrong.
        if token == None and (code == None or state == None):
            raise ValueError

        self.code = code
        self.state = state
        self.token = token

        self.is_oauth = code != None and state != None
        self.is_token = token != None
    
    def __eq__(self, other):
        if type(self) != type(other):
            return False

        return self.code == other.code and self.state == other.state and \
               self.token == other.token and self.is_oauth == other.is_oauth and \
               self.is_token == other.is_token


# Retrieve the User based on the login_id stored in the session
@login_manager.user_loader
def user_loader(login_id):
    db_user: User | None = get_user_by_login_id(login_id)

    if db_user == None:
        return None
    
    # Try to get the re-encrypted API keys
    # If they don't exist, invalidate the session
    if session['_id'] not in api_key_cache:
        # ATTENTION: If the session id is not saved in the api_key_cache, the user will need to login again
        # so that the session id and the tokens encryped with the session id can be stored in the cache.
        # Otherwise the user won't be able to use any endpoint as they would be logged in but without tokens in the cache.
        return None

    # Load cached values for the API tokens
    canvas_key, todoist_key = api_key_cache[session['_id']]
    db_user.canvas_token_session = canvas_key
    db_user.todoist_token_session = todoist_key

    return db_user

#################################################################
#                                                               #
#                     LOGIN, SIGNUP, LOGOUT                     #
#                                                               #
#################################################################

@auth.route('/login', methods=['POST'])
def login():

    with time_it('* Total time for LOGIN function:', ' seconds\n'):
        with time_it('\nLogin:'):
            # User is already logged in
            if current_user.is_authenticated:
                abort(HTTPStatus.UNAUTHORIZED)
                return
            
            parameters = _get_authentication_params(request, include_tokens=False)
            
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

        with time_it('Decrypting and Encrypting tokens:'):
            # Get the session identifier from the session
            # This is provided by Flask-Login as a unique identifer
            session_id = session['_id']

            # Decrypt tokens with password and re-encrypt with session_id
            session_canvas_token = reencrypt_str(db_user.canvas_token_password, password, session_id)
            session_todoist_token = reencrypt_str(db_user.todoist_token_password, password, session_id)

            # Cache API re-encrypted tokens for future requests
            api_key_cache[session_id] = (session_canvas_token, session_todoist_token)

    # Respond that the user was authenticated
    return jsonify({'success': True, 'message': f"Logged in as {db_user.username}"})


@auth.route('/signup', methods=['POST'])
def sign_up():

    parameters = _get_authentication_params(request, include_tokens=True)
    
    # Ensure the parameters were succesfully extracted from the body of the request
    if parameters is None:
        print('Invalid parameters')
        abort(HTTPStatus.BAD_REQUEST)
        return
    
    username, password, canvasToken, todoistInfo = parameters
    

    # If the username is invalid, determine it to be unprocessable
    # This is so that it is distinct from a bad request
    if not _is_valid_username(username):
        print('Invalid username')
        abort(HTTPStatus.BAD_REQUEST)
        return

    # If the password is invalid, determine it to be unprocessable
    # This is so that it is distinct from a bad request
    if not _is_valid_password(password):
        print('Invalid password')
        abort(HTTPStatus.BAD_REQUEST)
        return

    if todoistInfo.is_oauth:
        # Exchange the code and state for the Todoist Token
        exchange_response = exchange_token(todoistInfo.code, todoistInfo.state, session)
        if not exchange_response:
            print('Invalid token exchange')
            abort(HTTPStatus.BAD_REQUEST)
            return
        bearer, todoistToken = exchange_response    # Bearer is not needed right now, but in case we may need it in the future
    else:
        todoistToken = todoistInfo.token

    # Create the user, tokens are encrypted and password is hashed
    if not add_user(username, password, canvasToken, todoistToken):
        print('Invalid add user')
        abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        return
    
    # Respond that the user was created
    return jsonify({'success': True, 'message': f"Account created for {username}"}), 200

@auth.route('/change-password', methods=['POST'])
@login_required
def change_password():
    # Check if user is not authenticated
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'User is not authenticated'}), 401
    
    
    # New password must match the confirmed password
    old_password = request.json.get('oldPassword')
    new_password = request.json.get('newPassword')
    
    if len(new_password) > 128 or len(new_password) < 15:
        return jsonify({'success': False, 'message': "Password isn't between 15 and 128 characters"}), 400
    
    # Verify that the old password matches with the account hashed password
    try:
        password_hasher.verify(current_user.password, old_password)
    except VerifyMismatchError:
        return jsonify({'success': False, 'message': "Failed to update"}), 400
    
    if old_password == new_password:
        return jsonify({'success': False, 'message': "You can't insert the same password"}), 400
    
    # Update database with new password, rencrypt tokens, and new login id
    update_password(current_user, new_password, old_password)
    
    
    # Delete old session information from cache
    old_session_id = session.get('_id')
    if old_session_id:
        del api_key_cache[old_session_id]
    
    # Logout User
    logout_user()
    
    return jsonify({'success': True, 'message': 'Password changed successfully!'}), 200


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

def _get_authentication_params(request: Request, include_tokens: bool=False) -> tuple[str, str] | tuple[str, str, str, TodoistAuthInfo] |None:
    """
    Extracts the username and password from a request, if both exist and are valid.

    :param request: The Flask request to validate.
    :param include_tokens: If to extract the tokens from the request, will return a
    tuple[str, str, str, TodoistAuthInfo].
    :return tuple[str, str]: Returns the username and password if both exist and are valid and
    `include_tokens` is False.
    :return tuple[str, str, str, TodoistAuthInfo]: Returns the username, password, and the tokens if
    they all exist and are valid.
    :return None: Returns None if the username, password or the tokens don't exist or are invalid.
    """
    # There is no json data in the request
    if not request.json:
        return None

    # If the request json can't be parsed, return None
    username = request.json.get('username')
    password = request.json.get('password')

    if include_tokens:
        canvas_token = request.json.get('canvasToken')
        
        # Handle the case where OAuth is being used as well as a long term API key
        todoist_oauth_info = request.json.get('todoist')
        todoist_token = request.json.get('todoistToken')
        if type(todoist_oauth_info) == dict:
            todoist_code = todoist_oauth_info.get('code')
            todoist_state = todoist_oauth_info.get('state')
            todoist_auth = TodoistAuthInfo(todoist_code, todoist_state)
        elif type(todoist_token) == str:
            todoist_auth = TodoistAuthInfo(token=todoist_token)
        else:
            return None
        params = (username, password, canvas_token, todoist_auth)
    else:
        params = (username, password)

    # Check that all fields of params are strings or TodoistAuthInfo and not None
    if any(param is None or not isinstance(param, str|TodoistAuthInfo) for param in params):
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
