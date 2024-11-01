import argon2
import flask_login.utils
import pytest

from utils.crypto import encrypt_str

#################################################################
#                                                               #
#                           MOCK DATA                           #
#                                                               #
#################################################################


@pytest.fixture(autouse=True)
def init_test(monkeypatch):
    # Need to set TODOIST_SECRET before importing to ensure that it can read a fake Todoist secret
    monkeypatch.setenv('TODOIST_SECRET', '../../../secrets.example/todoist_secret.txt')


# Mocks flask.Request
class MockRequest:
    def __init__(self, json: dict):
        self.json = json


# Mocks flask_login.current_user
class MockCurrentUser:
    def __init__(self, is_authed: bool = False):
        self.is_authenticated = is_authed


# Mocks utils.models.User
class MockUser:
    def __init__(self, username, password, ctoken=None, ttoken=None):
        self.username = username
        self.password = password
        self.is_active = True
        if ctoken == None:
            self.canvas_token_password = encrypt_str('a'*69, password)
        else:
            self.canvas_token_password = encrypt_str(ctoken, password)
        if ttoken == None:
            self.todoist_token_password = encrypt_str('a'*40, password)
        else:
            self.todoist_token_password = encrypt_str(ttoken, password)

    # Allow conversion to dict
    def __iter__(self):
        yield "username", self.username
        yield "password", self.password


# Mocks utils.queries.password_hasher
class MockPasswordHasher:
    def verify(self, hash: str | bytes, password: str | bytes):
        if hash == password:
            return True

        raise argon2.exceptions.VerifyMismatchError

    def hash(self, password: str | bytes, salt: bytes | None = None):
        return password


# Mocks flask.session
class MockSession:
    def __init__(self):
        self.data = {'_id': 'id'}

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value


# Mocks User table
users = [
    MockUser("user", "pass"),
    MockUser("a", "b"),
    MockUser("admin", "admin")
]


def mock_get_user_by_username(username: str, dict: bool = False) -> MockUser | dict | None:
    selected_user = None
    for user in users:
        if user.username == username:
            selected_user = user
            break

    if selected_user == None:
        return None

    if dict:
        return dict(selected_user)
    return selected_user


def mock_abort(status):
    global abort_status
    abort_status = status


def mock_login_user(_):
    global is_logged_in
    is_logged_in = True


def mock_get_user():
    return MockCurrentUser()


def mock_add_user(username, password, canvasToken, todoistToken):
    for user in users:
        if user.username == username:
            return False

    users.append(MockUser(username, password, canvasToken, todoistToken))
    return True


def mock_exchange_token(code, state, session):
    return 'bearer', 'ttoken'

#################################################################
#                                                               #
#                           UNIT TESTS                          #
#                                                               #
#################################################################


def test_get_authentication_params_no_tokens():
    import api.auth.authentication as authentication

    # Test empty request
    req = MockRequest({})
    assert authentication._get_authentication_params(req, include_tokens=False) == None

    # Test missing password
    req = MockRequest({"username": "user"})
    assert authentication._get_authentication_params(req, include_tokens=False) == None

    # Test missing username
    req = MockRequest({"password": "pass"})
    assert authentication._get_authentication_params(req, include_tokens=False) == None

    # Test wrong type for username
    req = MockRequest({"username": 1, "password": "pass"})
    assert authentication._get_authentication_params(req, include_tokens=False) == None

    # Test wrong type for password
    req = MockRequest({"username": "user", "password": 2})
    assert authentication._get_authentication_params(req, include_tokens=False) == None

    # Test valid username and password
    req = MockRequest({"username": "user", "password": "pass"})
    assert authentication._get_authentication_params(req, include_tokens=False) == ("user", "pass")

    # Test extra parameters
    req = MockRequest({"username": "user", "password": "pass", "canvasToken": "token",
                       "todoistToken": "token"})
    assert authentication._get_authentication_params(req, include_tokens=False) == ("user", "pass")


def test_get_authentication_params_tokens():
    import api.auth.authentication as authentication

    # Missing info

    # Test empty request
    req = MockRequest({})
    assert authentication._get_authentication_params(req, include_tokens=True) == None

    # Test missing password
    req = MockRequest({"username": "user", "canvasToken": "token", "todoistToken": "token"})
    assert authentication._get_authentication_params(req, include_tokens=True) == None

    # Test missing username
    req = MockRequest({"password": "pass", "canvasToken": "token", "todoistToken": "token"})
    assert authentication._get_authentication_params(req, include_tokens=True) == None

    # Test missing Canvas token
    req = MockRequest({"username": "user", "password": "pass", "todoistToken": "token"})
    assert authentication._get_authentication_params(req, include_tokens=True) == None

    # Test missing todoistToken info
    req = MockRequest({"username": "user", "password": "pass", "canvasToken": "token"})
    assert authentication._get_authentication_params(req, include_tokens=True) == None

    # Test missing todoistToken.code
    req = MockRequest({"username": "user", "password": "pass", "canvasToken": "token",
                       "todoistToken": {"state": "state"}})
    assert authentication._get_authentication_params(req, include_tokens=True) == None

    # Test missing todoistToken.state
    req = MockRequest({"username": "user", "password": "pass", "canvasToken": "token",
                       "todoistToken": {"code": "code"}})
    assert authentication._get_authentication_params(req, include_tokens=True) == None

    # Wrong types

    # Test wrong type for username
    req = MockRequest({"username": 1, "password": "pass", "canvasToken": "token",
                       "todoistToken": "token"})
    assert authentication._get_authentication_params(req, include_tokens=True) == None

    # Test wrong type for password
    req = MockRequest({"username": "user", "password": 1, "canvasToken": "token",
                       "todoistToken": "token"})
    assert authentication._get_authentication_params(req, include_tokens=True) == None

    # Test wrong type for canvasToken
    req = MockRequest({"username": "user", "password": "pass", "canvasToken": 1,
                       "todoistToken": "token"})
    assert authentication._get_authentication_params(req, include_tokens=True) == None

    # Test wrong type for todoist (OAuth)
    req = MockRequest({"username": "user", "password": "pass", "canvasToken": "token",
                       "todoist": "not a dict"})
    assert authentication._get_authentication_params(req, include_tokens=True) == None

    # Test wrong type for todoistToken (permanent API key)
    req = MockRequest({"username": "user", "password": "pass", "canvasToken": "token",
                       "todoistToken": 1})
    assert authentication._get_authentication_params(req, include_tokens=True) == None

    # Valid info

    # Test Todoist OAuth
    req = MockRequest({"username": "user", "password": "pass", "canvasToken": "token",
                       "todoist": {"state": "state", "code": "code"}})
    assert authentication._get_authentication_params(req, include_tokens=True) == \
        ("user", "pass", "token", authentication.TodoistAuthInfo("code", "state"))

    # Test Todoist token
    req = MockRequest({"username": "user", "password": "pass", "canvasToken": "ctoken",
                       "todoistToken": "ttoken"})
    assert authentication._get_authentication_params(req, include_tokens=True) == \
        ("user", "pass", "ctoken", authentication.TodoistAuthInfo(token="ttoken"))


is_logged_in = False
abort_status = None


def test_login(monkeypatch):
    global is_logged_in, abort_status
    import api.auth.authentication as authentication

    monkeypatch.setattr(flask_login.utils, "_get_user", mock_get_user)
    monkeypatch.setattr(authentication, "get_user_by_username", mock_get_user_by_username)
    monkeypatch.setattr(authentication, "password_hasher", MockPasswordHasher())
    monkeypatch.setattr(authentication, "login_user", mock_login_user)
    monkeypatch.setattr(authentication, "session", MockSession())
    # Return objects as objects not strs
    monkeypatch.setattr(authentication, "jsonify", lambda x: x)
    monkeypatch.setattr(authentication, "abort", mock_abort)

    # Test missing username
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"password": "pass"}))
    authentication.login()
    assert is_logged_in == False
    assert abort_status == 400

    # Test missing password
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"password": "user"}))
    authentication.login()
    assert is_logged_in == False
    assert abort_status == 400

    # Test invalid username
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "fake", "password": "user"}))
    authentication.login()
    assert is_logged_in == False
    assert abort_status == 401

    # Test invalid password
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "user", "password": "fake"}))
    authentication.login()
    assert is_logged_in == False
    assert abort_status == 401

    # Test valid login
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "user", "password": "pass"}))
    resp = authentication.login()
    assert resp['success'] == True
    assert resp['message'] == 'Logged in as user'

    # Check the user was logged in and reset the flag
    assert is_logged_in
    is_logged_in = False

    # Test second valid login
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "a", "password": "b"}))
    resp = authentication.login()
    assert resp['success'] == True
    assert resp['message'] == 'Logged in as a'

    # Check the user was logged in and reset the flag
    assert is_logged_in
    is_logged_in = False


def test_sign_up(monkeypatch):
    global abort_status
    import api.auth.authentication as authentication

    monkeypatch.setattr(authentication, "abort", mock_abort)
    monkeypatch.setattr(authentication, "add_user", mock_add_user)
    # Return objects as objects not strs
    monkeypatch.setattr(authentication, "jsonify", lambda x: x)
    monkeypatch.setattr(authentication, "exchange_token", mock_exchange_token)

    # Test sign up missing username
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"password": "passwordpassword",
                                     "canvasToken": "ctoken", "todoistToken": "ttoken"}))
    authentication.sign_up()
    assert abort_status == 400

    # Test sign up missing password
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "newuser",
                                     "canvasToken": "ctoken", "todoistToken": "ttoken"}))
    authentication.sign_up()
    assert abort_status == 400
    assert mock_get_user_by_username("newuser") == None

    # Test sign up missing Canvas token
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "newuser", "password": "passwordpassword",
                                     "todoistToken": "ttoken"}))
    authentication.sign_up()
    assert abort_status == 400
    assert mock_get_user_by_username("newuser") == None

    # Test sign up missing Todoist info
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "newuser", "password": "passwordpassword",
                                     "canvasToken": "ctoken"}))
    authentication.sign_up()
    assert abort_status == 400
    assert mock_get_user_by_username("newuser") == None

    # Test sign up with invalid username
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "", "password": "password",
                                     "canvasToken": "ctoken", "todoistToken": "ttoken"}))
    authentication.sign_up()
    assert abort_status == 400
    assert mock_get_user_by_username("") == None

    # Test sign up with invalid password
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "newuser", "password": 2,
                                     "canvasToken": "ctoken", "todoistToken": "ttoken"}))
    authentication.sign_up()
    assert abort_status == 400
    assert mock_get_user_by_username("newuser") == None

    # Test sign up with invalid Canvas token
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "newuser", "password": "password",
                                     "canvasToken": 3, "todoistToken": "ttoken"}))
    authentication.sign_up()
    assert abort_status == 400
    assert mock_get_user_by_username("newuser") == None

    # Test sign up with invalid Todoist token
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "newuser", "password": "password",
                                     "canvasToken": "ctoken", "todoistToken": 4}))
    authentication.sign_up()
    assert abort_status == 400
    assert mock_get_user_by_username("newuser") == None

    # Test sign up with invalid Todoist OAuth info
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "newuser", "password": "password",
                                     "canvasToken": "ctoken", "todoist": 5}))
    authentication.sign_up()
    assert abort_status == 400
    assert mock_get_user_by_username("newuser") == None

    # Test sign up with insecure password
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "newuser", "password": "password",
                                     "canvasToken": "ctoken", "todoistToken": "ttoken"}))
    authentication.sign_up()
    assert abort_status == 400
    assert mock_get_user_by_username("newuser") == None

    # Test sign up with duplicate username
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "user", "password": "passwordpassword",
                                     "canvasToken": "ctoken", "todoistToken": "ttoken"}))
    authentication.sign_up()
    assert abort_status == 500

    # Test valid sign up with OAuth Todoist
    toauth = {"code": "code", "state": "state"}
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "oauth", "password": "passwordpassword",
                                     "canvasToken": "ctoken", "todoist": toauth}))
    resp, status = authentication.sign_up()
    assert resp['success'] == True
    assert 'oauth' in resp['message']
    assert status == 200
    assert mock_get_user_by_username('oauth').username == 'oauth'

    # Test valid sign up with long-term Todoist token
    monkeypatch.setattr(authentication, "request",
                        MockRequest({"username": "token", "password": "passwordpassword",
                                     "canvasToken": "ctoken", "todoistToken": "ttoken"}))
    resp, status = authentication.sign_up()
    assert resp['success'] == True
    assert 'token' in resp['message']
    assert status == 200
    assert mock_get_user_by_username('token').username == 'token'
