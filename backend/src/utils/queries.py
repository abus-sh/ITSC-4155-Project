#########################################################################
#                                                                       #
#    This is just an EXAMPLE of how we may structure it. This file      #
#    will contain the functions for querying the database.              #
#                                                                       #
#########################################################################
from utils.models import *
from utils.crypto import encrypt_str
from canvasapi import Canvas
from todoist_api_python.api import TodoistAPI
from requests.exceptions import HTTPError

def add_user(username: str, password: str, canvas_token: str, todoist_token: str) -> bool:
    """
    Add a new user to the database. Encrypt the tokens and then hash the password with argon2.

    :param username: The user's username, must be unique.
    :param password: The user's hashed password.
    :param canvas_key: The user's Canvas API key.
    :param todoist_key: The user's Todoist API key.
    :return bool: Returns True if the user was added, False otherwise.
    """
    try:
        # Check that the Canvas token is valid
        canvas_user = Canvas('https://uncc.instructure.com', canvas_token).get_current_user()
        canvas_id = getattr(canvas_user, 'id', None)
        canvas_name = getattr(canvas_user, 'name', None)
        if canvas_id is None or canvas_name is None:
            return False
        
        # Check that the Todoist token is valid
        try:
            # This will almost certainly fail, but the way it fails will show if the token is valid
            # If it happens to succeed, then that means the token is valid
            TodoistAPI(todoist_token).get_task(task_id='0')
        except HTTPError as ex:
            # 401 indicates Forbidden, API key is bad
            # Non-401 error indicates that the API key is good
            if ex.response.status_code == 401:
                return False

        
        # This Canvas user is already associated with an existing user (prevents multiple account with different tokens)
        if User.query.filter_by(canvas_id=canvas_id).first():
            return False
        
        # Encrypt canvas and todoist token with password
        canvas_token_password = encrypt_str(canvas_token, password).to_bytes()
        todoist_token_password = encrypt_str(todoist_token, password).to_bytes()

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


def add_or_return_task(owner: User|int, canvas_id: str, todoist_id: str|None=None, due_date: str=None) -> Task:
    """
    Add a new task to the database or return the task if it already exists.

    :param owner: The User or the ID of the User who owns the task.
    :param canvas_id: The ID of the task in Canvas. This can be found with the Canvas API.
    :param todoist_id: The ID of the task in Todoist, if a task exists. If no ID is provided, no
    Todoist task is linked to the Canvas task at this time.
    :return Task: The Task that was added.
    :raises Exception: If the Task could not be added to the database.
    """
    # TODO: make :rasies Exception: more specific.
    if type(owner) == User:
        owner = owner.id

    # Prevent exact duplicates from being registered.
    current_task = Task.query.filter_by(owner=owner, canvas_id=canvas_id).first()
    if current_task:
        return current_task

    try:
        new_task = Task(owner=owner, task_type=TaskType.assignment, canvas_id=canvas_id,
                        todoist_id=todoist_id, due_date=due_date)
        db.session.add(new_task)
        db.session.commit()
        return new_task
    except Exception as e:
        db.session.rollback()
        print(f"Error adding task: {e}")
        raise e


def set_todoist_task(task: Task, todoist_id: str) -> None:
    """
    Update a task to reference a Todoist task.

    :param Task: A Task in the database.
    :param todoist_id: The ID of a task in Todoist.
    """
    try:
        task.todoist_id = todoist_id
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error updating task: {e}")
        raise e
    
def update_task_duedate(task: Task, due_date: str) -> None:
    """
    Update a task to have a new due_date in the database

    :param Task: A Task in the database.
    :param due_date: The updated due_date of the task.
    """
    try:
        task.due_date = due_date
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error updating task: {e}")
        raise e


def get_task_by_canvas_id(owner: User|int, canvas_id: str, dict=False) -> Task | dict | None:
    """
    Retrieve a task by its Canvas ID, which is assigned by Canvas.

    :param owner: The User or the ID of the User who owns the task.
    :param canvas_id: The internal Canvas ID of a task.
    :param dict: If True, return the user as a dictionary. Defaults to False.
    :return Task or dict or None: A Task instance or a dictionary representation of the task if dict
    is True. If no task with the given Canvas ID exists, None is returned.
    """
    if type(owner) == User:
        owner = owner.id

    task = Task.query.filter_by(owner=owner, canvas_id=canvas_id).first()
    if dict and task:
        return task.to_dict()
    return task

