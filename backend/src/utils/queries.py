
#########################################################################
#                                                                       #
#    This is just an EXAMPLE of how we may structure it. This file      #
#    will contain the functions for querying the database.              #
#                                                                       #
#########################################################################
from utils.models import *

def add_user(name: str, primary_email: str, secondary_email: str=None) -> None:
    """
    Add a new user to the database.

    :param name: The user's name.
    :param primary_email: The user's primary email, must be unique.
    :param secondary_email: The user's seconday email.
    """
    try:
        new_user = User(name=name, primary_email=primary_email, secondary_email=secondary_email)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error adding user: {e}")


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


def get_user_by_email(primary_email: str, dict=False) -> User | dict:
    """
    Retrieve a user by their primary email.

    :param primary_email: The primary email of the user to retrieve.
    :param dict: If True, return the user as a dictionary. Defaults to False.
    :return user or dict: A User instance or a dictionary representation of the user if dict is True.
    """
    user = User.query.filter_by(primary_email=primary_email).first()
    if dict and user:
        return user.to_dict()
    return user

