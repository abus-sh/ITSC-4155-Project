#########################################################################
#                                                                       #
#    This is just an EXAMPLE of how we may structure it. This file      #
#    will contain the functions for querying the database.              #
#                                                                       #
#########################################################################
from utils.models import *

def add_user(username: str, password: str) -> bool:
    """
    Add a new user to the database.

    :param username: The user's username, must be unique.
    :param password: The user's hashed password.
    :return bool: Returns True if the user was added, False otherwise.
    """
    try:
        # If the username already exists
        if get_user_by_username(username):
            return False
        
        new_user = User(username=username, password=password)
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

def get_user_by_login_id(username: str, dict=False) -> User | dict:
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

