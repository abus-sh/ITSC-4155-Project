import pytest
import os

os.environ['TODOIST_SECRET'] = 'secrets.example/todoist_secret.txt'
os.environ['DB_CONN_FILE'] = 'secrets.example/connection_string.txt'
os.environ['SESSION_SECRET_FILE'] = 'secrets.example/session_secret.txt'
os.environ['TODO_SECRET_FILE'] = 'secrets.example/todoist_secret_encrypt.txt'
os.environ['CSRF'] = 'OFF'

import app as app_mod  # noqa: E402


@pytest.fixture
def app():
    app_mod.app.debug = True
    return app_mod.app
