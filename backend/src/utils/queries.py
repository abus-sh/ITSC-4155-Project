#########################################################################
#                                                                       #
#    This is just an EXAMPLE of how we may structure it. This file      #
#    will contain the functions for querying the database.              #
#                                                                       #
#########################################################################
from utils.models import *
from canvasapi import Canvas

def add_user(username: str, password: str, canvas_token: str, todoist_token: str) -> bool:
    """
    Add a new user to the database. Encrypt the tokens and then hash the password with argon2.

    :param username: The user's username, must be unique.
    :param password: The user's hashed password.
    :param canvas_key: The user's encrypted Canvas API key.
    :param todoist_key: The user's encrypted Todoist API key.
    :return bool: Returns True if the user was added, False otherwise.
    """
    try:
        # Check that the Canvas token is valid
        canvas_user = Canvas("https://uncc.instructure.com", canvas_token).get_current_user()
        canvas_id = getattr(canvas_user, 'id', None)
        canvas_name = getattr(canvas_user, 'name', None)
        if canvas_id is None or canvas_name is None:
            return False
        
        # Check that the Todoist token is valid
        # TODO: check todoist token
        
        # This Canvas user is already associated with an existing user (prevents multiple account with different tokens)
        if User.query.filter_by(canvas_id=canvas_id).first():
            return False
        
        # Encrypt canvas and todoist token with password
        # TODO: encrypt tokens
        canvas_token_password = canvas_token
        todoist_token_password = todoist_token

        # Hash the password
        pw_hash = password_hasher.hash(password)

        new_user = User(login_id=gen_unique_login_id(), username=username, password=pw_hash,
                        canvas_id=canvas_id, canvas_name=canvas_name,
                        canvas_token_password=canvas_token_password, todoist_token_password=todoist_token_password)
        db.session.add(new_user)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error adding user: {e}")
        return False


def get_all_users() -> list[User]:
    """
    Retrieve all users from the database.

    :return list: A list of all User instances.
    """
    return User.query.all()


def get_user_by_id(user_id: int, dict=False) -> User | dict:
    """
    Retrieve a user by their ID.

    :param user_id: The id of the user to retrieve.
    :param dict: If True, return the user as a dictionary. Defaults to False.
    :return user or dict: A user instance or a dictionary representation of the user if dict is True.
    """
    user = User.query.get(user_id)
    if dict and user:
        return user.to_dict()
    return user


def get_user_by_username(username: str, dict=False) -> User | dict:
    """
    Retrieve a user by their username.

    :param username: The username of the user to retrieve.
    :param dict: If True, return the user as a dictionary. Defaults to False.
    :return User or dict or None: A User instance or a dictionary representation of the user if dict
    is True. If no user with the given username exists, None is returned.
    """
    user = User.query.filter_by(username=username).first()
    if dict and user:
        return user.to_dict()
    return user

def get_user_by_login_id(login_id: str, dict=False) -> User | dict | None:
    """
    Retrieve a user by their login_id.

    :param login_id: The login_id of the user to retrieve.
    :param dict: If True, return the user as a dictionary. Defaults to False.
    :return User or dict or None: A User instance or a dictionary representation of the user if dict
    is True. If no user with the given username exists, None is returned.
    """
    user = User.query.filter_by(login_id=login_id).first()
    if dict and user:
        return user.to_dict()
    return user

