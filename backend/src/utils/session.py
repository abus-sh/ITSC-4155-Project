"""
This file provides utilities for reading data from the session. This includes functions that rely on
application-specific state, such as the `User` class.
"""


from flask import session
from flask_login import current_user

from utils.crypto import decrypt_str


def decrypt_api_keys() -> tuple[str, str]:
    """
    Decrypts the API keys for the current user. Returns them as (canvas_key, todoist_key).

    :return tuple[str, str]: The Canvas API key and the Todoist API key.
    :raises ValueError: If session does not have an _id or current_user has no encrypted API keys.
    """
    # If the session doesn't have an ID, can't decrypt keys
    if '_id' not in session:
        raise ValueError
    session_id = session['_id']

    # If current user doesn't have API keys encrypted w/ session key, can't decrypt keys
    if current_user.canvas_token_session is None or current_user.todoist_token_session is None:
        raise ValueError

    canvas_token = decrypt_str(current_user.canvas_token_session, session_id)
    todoist_token = decrypt_str(current_user.todoist_token_session, session_id)

    return (canvas_token, todoist_token)


def decrypt_canvas_key() -> str:
    """
    Decrypts the Canvas API keys for the current user.

    :returns str: The Canvas API key.
    :raises ValueError: If session does not have an _id or current_user has no encrypted Canvas API
    key.
    """
    # If the session doesn't have an ID, can't decrypt key
    if '_id' not in session:
        raise ValueError
    session_id = session['_id']

    # If current user doesn't have a Canvas API key encrypted w/ session key, can't decrypt key
    if current_user.canvas_token_session is None:
        raise ValueError

    return decrypt_str(current_user.canvas_token_session, session_id)


def decrypt_todoist_key() -> str:
    """
    Decrypts the Todoist API keys for the current user.

    :returns str: The Todoist API key.
    :raises ValueError: If session does not have an _id or current_user has no encrypted Todoist API
    key.
    """
    # If the session doesn't have an ID, can't decrypt key
    if '_id' not in session:
        raise ValueError
    session_id = session['_id']

    # If current user doesn't have a Canvas API key encrypted w/ session key, can't decrypt key
    if current_user.todoist_token_session is None:
        raise ValueError

    return decrypt_str(current_user.todoist_token_session, session_id)
