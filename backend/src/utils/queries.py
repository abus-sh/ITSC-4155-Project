import utils.models as models
from utils.crypto import decrypt_str, encrypt_str, get_todo_secret
from canvasapi import Canvas
from todoist_api_python.api import TodoistAPI
from requests.exceptions import HTTPError
from sqlalchemy import select, or_
import sqlalchemy.exc
from datetime import datetime

#########################################################################
#                                                                       #
#                                USERS                                  #
#                                                                       #
#########################################################################


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

        # This Canvas user is already associated with an existing user (prevents multiple account
        # with different tokens)
        if models.User.query.filter_by(canvas_id=canvas_id).first():
            return False

        # Encrypt canvas and todoist token with password
        canvas_token_password = encrypt_str(canvas_token, password).to_bytes()
        todoist_token_password = encrypt_str(todoist_token, get_todo_secret()).to_bytes()

        # Hash the password
        pw_hash = models.password_hasher.hash(password)

        new_user = models.User(login_id=models.gen_unique_login_id(), username=username,
                               password=pw_hash, canvas_id=canvas_id, canvas_name=canvas_name,
                               canvas_token_password=canvas_token_password,
                               todoist_token_password=todoist_token_password)
        models.db.session.add(new_user)
        models.db.session.commit()
        return True
    except Exception as e:
        models.db.session.rollback()
        print(f"Error adding user: {e}")
        return False


def does_username_exists(username: str) -> bool:
    """
    Check if a user with the given username exists in the database.

    :param username: The username to check.
    :return bool: Returns True if the user exists, False otherwise.
    """
    return models.User.query.filter_by(username=username).first() is not None


def update_password(user: models.User, new_password: str, old_password: str):
    try:
        # Re-encrypt token with new password
        plain_canvas_token = decrypt_str(user.canvas_token_password, old_password)
        plain_todoist_token = decrypt_str(user.todoist_token_password, old_password)
        user.canvas_token_password = encrypt_str(plain_canvas_token, new_password).to_bytes()
        user.todoist_token_password = encrypt_str(plain_todoist_token, new_password).to_bytes()

        # Hash new password
        user.password = models.password_hasher.hash(new_password)
        # New login id, makes previous session tokens invalid
        user.login_id = models.gen_unique_login_id()

        models.db.session.commit()
    except Exception as e:
        models.db.session.rollback()
        print("Error: ", e)


def get_all_users() -> list[models.User]:
    """
    Retrieve all users from the database.

    :return list: A list of all User instances.
    """
    return models.User.query.all()


def get_user_by_id(user_id: int, dict=False) -> models.User | dict:
    """
    Retrieve a user by their ID.

    :param user_id: The id of the user to retrieve.
    :param dict: If True, return the user as a dictionary. Defaults to False.
    :return user or dict: A user instance or a dictionary representation of the user if dict is
    True.
    """
    user = models.User.query.get(user_id)
    if dict and user:
        return user.to_dict()
    return user


def get_user_todoist_api(user_id: int) -> str | None:
    """
    Retrieve a user's Todoist encrypted API key by their ID.

    :param user_id: The id of the user to retrieve.
    :return str | None: The Todoist encrypted API key of the user, None if user doesn't exist.
    """
    user = models.User.query.get(user_id)
    if user:
        return user.todoist_token_password
    return None


def get_user_by_username(username: str, dict=False) -> models.User | dict:
    """
    Retrieve a user by their username.

    :param username: The username of the user to retrieve.
    :param dict: If True, return the user as a dictionary. Defaults to False.
    :return User or dict or None: A User instance or a dictionary representation of the user if dict
    is True. If no user with the given username exists, None is returned.
    """
    user = models.User.query.filter_by(username=username).first()
    if dict and user:
        return user.to_dict()
    return user


def get_user_by_login_id(login_id: str, dict=False) -> models.User | dict | None:
    """
    Retrieve a user by their login_id.

    :param login_id: The login_id of the user to retrieve.
    :param dict: If True, return the user as a dictionary. Defaults to False.
    :return User or dict or None: A User instance or a dictionary representation of the user if dict
    is True. If no user with the given username exists, None is returned.
    """
    user = models.User.query.filter_by(login_id=login_id).first()
    if dict and user:
        return user.to_dict()
    return user


#########################################################################
#                                                                       #
#                                TASKS                                  #
#                                                                       #
#########################################################################


def add_or_return_task(owner: models.User | int, canvas_id: str | None,
                       todoist_id: str | None = None, due_date: str = None, name: str | None = None,
                       desc: str | None = None) -> models.Task:
    """
    Add a new task to the database or return the task if it already exists.

    :param owner: The User or the ID of the User who owns the task.
    :param canvas_id: The ID of the task in Canvas, optionally. This can be found with the Canvas
    API.
    :param todoist_id: The ID of the task in Todoist, if a task exists. If no ID is provided, no
    Todoist task is linked to the Canvas task at this time.
    :return Task: The Task that was added.
    :raises Exception: If the Task could not be added to the database.
    """
    # TODO: make :rasies Exception: more specific.
    user_id = getattr(owner, 'id', None)
    if user_id:
        owner = user_id

    # Prevent exact duplicates from being registered.
    if canvas_id:
        current_task = models.Task.query.filter_by(owner=owner, canvas_id=canvas_id).first()
        if current_task:
            return current_task

    try:
        new_task = models.Task(owner=owner, task_type=models.TaskType.assignment,
                               canvas_id=canvas_id, todoist_id=todoist_id, due_date=due_date,
                               name=name, description=desc)
        models.db.session.add(new_task)
        models.db.session.commit()
        return new_task
    except Exception as e:
        models.db.session.rollback()
        print(f"Error adding task: {e}")
        raise e


def update_task_id(primary_key: str, todoist_id: str) -> None:
    """
    Update a task to reference a Todoist task.

    :param task_id: The primary key of a Task in the database.
    :param todoist_id: The ID of a task in Todoist.
    """
    try:
        task = models.Task.query.get(primary_key)
        if task:
            task.todoist_id = todoist_id
            models.db.session.commit()
    except Exception as e:
        models.db.session.rollback()
        print(f"Error updating task: {e}")
        raise e


def update_task_description(task: models.Task, description: str) -> None:
    """
    Update a task's description in the database.

    :param id: The internal database ID of the task.
    :param description: The new description for the task.
    """
    try:
        task.description = description
        models.db.session.commit()
    except Exception as e:
        models.db.session.rollback()
        print('Error updating description', {e})
        raise e


def set_task_duedate(task: models.Task, due_date: str) -> None:
    """
    Update a task to have a new due_date in the database

    :param Task: A Task in the database.
    :param due_date: The updated due_date of the task.
    """
    try:
        task.due_date = due_date
        models.db.session.commit()
    except Exception as e:
        models.db.session.rollback()
        print(f"Error updating task: {e}")
        raise e


def get_task_by_id(owner: models.User, id: int, dict=False) -> models.Task | dict | None:
    """
    Retrieve a task by its database ID.

    :param owner: The owner of the task.
    :param canvas_id: The database ID of a task.
    :param dict: If True, return the task as a dictionary. Defaults to False.
    :return Task or dict or None: A Task instance or a dictionary representation of the task if dict
    is True. If no task with the given Canvas ID exists, None is returned.
    """

    task = models.Task.query.filter(
        models.Task.id == id,
        models.Task.owner == owner.id
    ).first()
    if dict and task:
        return task.to_dict()
    return task


def get_task_by_canvas_id(owner: models.User, canvas_id: str, dict=False)\
        -> models.Task | dict | None:
    """
    Retrieve a task by its Canvas ID, which is assigned by Canvas.

    :param owner: The owner of the task.
    :param canvas_id: The internal Canvas ID of a task.
    :param dict: If True, return the task as a dictionary. Defaults to False.
    :return Task or dict or None: A Task instance or a dictionary representation of the task if dict
    is True. If no task with the given Canvas ID exists, None is returned.
    """

    task = models.Task.query.filter(
        models.Task.canvas_id == canvas_id,
        models.Task.owner == owner.id
    ).first()
    if dict and task:
        return task.to_dict()
    return task


def get_non_canvas_tasks(owner: models.User, dict=False) -> list[models.Task] | list[dict]:
    """
    Retrieves all tasks that do not have a Canvas ID and that are due in the future.

    :param owner: The owner of the tasks.
    :param dict: If True, return the tasks as a list of dictionaries. Defaults to False.
    :return list[Task] or list[dict]: A list of Tasks that have no Canvas ID or a list of the Tasks
    as dicts if dict is True.
    """

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    tasks = models.Task.query.filter(
        models.Task.owner == owner.id,
        models.Task.canvas_id == None,  # noqa: E711, using 'is' breaks comparison here
        models.Task.due_date > now
    ).all()
    if dict:
        return [dict(task) for task in tasks]
    return tasks


def get_task_or_subtask_by_todoist_id(owner: models.User, todoist_id: str, dict=False)\
        -> models.Task | models.SubTask | dict | None:
    """
    Retrieve a task or subtask by its Todoist ID.

    :param owner: The owner of the task.
    :param canvas_id: The internal Todoist ID of a task or subtask.
    :param dict: If True, return the task or subtask as a dictionary. Defaults to False.
    :return Task | SubTask: The task or subtask that was retrieved, assuming dict is False.
    :return dict: The task or subtask that was retrieved, assuming dict is True.
    :return None: Indicates that no task or subtask with the given ID was found.
    """

    # Check for a matching task first
    task = models.Task.query.filter(
        models.Task.todoist_id == todoist_id,
        models.Task.owner == owner.id
    ).first()
    if task:
        if dict:
            return dict(task)
        else:
            return task

    # Check for a matching subtask
    subtask = models.SubTask.query.filter(
        or_(
            models.SubTask.owner == owner.id,
            models.SubTask.shared_with.contains([owner.id])
        ),
        models.SubTask.todoist_id == todoist_id
    ).first()
    if subtask:
        if dict:
            return dict(subtask)
        else:
            return subtask

    # If neither were found, return None
    return None


def get_descriptions_by_canvas_ids(owner: models.User, canvas_ids: list[int])\
        -> dict[int, str | None]:
    """
    Retrieves descriptions for all tasks with the Canvas IDs specified in `canvas_ids` and returns
    a dict that maps between the ids and the descriptions.

    :param owner: The owner of the tasks.
    :param canvas_ids: The Canvas IDs of the tasks that should have descriptions retrieved.
    :return dict[int, str|None]: Returns a dict that maps between the ids and the descriptions. If a
    task has no description, its entry is None.
    """
    canvas_tasks: list[models.Task] = models.Task.query.filter(
        models.Task.canvas_id.in_(canvas_ids),
        models.Task.owner == owner.id
    ).all()

    description_lookup = dict()
    for task in canvas_tasks:
        description_lookup[task.canvas_id] = task.description

    return description_lookup


def sync_task_status(owner: models.User, open_task_ids: list[int]) -> None:
    """
    Sets the status for all tasks. Any task ID in open_task_ids will be set to incomplete and
    all others will be set to completed.

    :param owner: The owner of the tasks.
    :param open_task_ids: The IDs of the tasks that should be in progress.
    """
    # Handle tasks
    try:
        tasks: list[tuple[models.Task]] = models.db.session\
            .execute(select(models.Task).where(models.Task.owner == owner.id))
        for (task,) in tasks:
            if task.todoist_id in open_task_ids:
                task.status = models.TaskStatus.Incomplete
            else:
                print(f'Marking task {task.todoist_id} as done')
                task.status = models.TaskStatus.Completed
        models.db.session.commit()
    except Exception as e:
        print("Task rollback", e)
        models.db.session.rollback()

    shared_subtasks = []
    
    # Handle subtasks
    try:
        tasks: list[tuple[models.SubTask]] = models.db.session\
            .execute(select(models.SubTask).where(models.SubTask.owner == owner.id))
        for (task,) in tasks:
            if task.todoist_id in open_task_ids:
                task.status = models.TaskStatus.Incomplete
            else:
                print(f'Marking task {task.todoist_id} as done')
                task.status = models.TaskStatus.Completed
        models.db.session.commit()
        return shared_subtasks
    except Exception as e:
        print("Subtask rollback", e)
        models.db.session.rollback()


def send_subtask_invitation(owner: models.User, recipient: str, task_id: int, subtask_id: int) -> bool:
    """
    Send an invitation to a user to join a subtask.
    
    :param owner: The owner of the task.
    :param recipient: The username of the recipient.
    :param task_id: The ID of the task.
    :param subtask_id: The ID of the subtask.
    :return bool: True if the invitation was sent, False otherwise.
    """
    recipient = models.User.query.filter_by(username=recipient).first()
    subtask = models.SubTask.query.get(subtask_id)
    if not recipient or not subtask or subtask.owner != owner.id:
        return False
    
    recipient_has_task = models.Task.query.filter_by(owner=recipient.id, canvas_id=subtask.task.canvas_id).first()
    if not recipient_has_task:
        return False
    
    task_invitation = models.SubTaskInvitation(owner=owner.id, recipient=recipient.id, task_id=task_id, subtask_id=subtask_id)    
    models.db.session.add(task_invitation)
    models.db.session.commit()


def get_subtask_invitations(recipient: models.User, dict=False) -> list[models.SubTaskInvitation] | list[dict]:
    """
    Retrieve all subtask invitations for a user.
    
    :param recipient: The recipient of the subtask invitations.
    :param dict: If True, return the subtask invitations as a list of dictionaries. Defaults to False.
    :return list[TaskInvitation] or list[dict]: A list of subtask invitations or a list of dictionaries
    if dict is True.
    """
    invitations = models.SubTaskInvitation.query.filter_by(recipient=recipient.id).all()
    if dict:
        return [invitation.to_dict() for invitation in invitations]
    return invitations


def get_shared_subtasks(owner: models.User, dict=False) -> list[models.SubTask] | list[dict]:
    """
    Retrieve all shared subtasks for a user.
    
    :param owner: The owner of the subtasks.
    :param dict: If True, return the subtasks as a list of dictionaries. Defaults to False.
    :return list[SubTask] or list[dict]: A list of shared subtasks or a list of dictionaries
    if dict is True.
    """
    shared_subtasks = models.SubTaskShared.query.filter_by(owner=owner.id).all()
    if dict:
        return [subtask.to_dict() for subtask in shared_subtasks]
    return shared_subtasks


def get_shared_users_subtask(subtask: models.SubTask) -> list[int, str] | None:
    """
    This function retrieve all the users a shared subtask has been shared with (including the original owner).
    Together with their todoist ID for the shared subtask in their todoist.
    
    """
    all_users = subtask.shared_with
    if not isinstance(all_users, list):
        return None
    all_users.append(subtask.owner)
    
    user_todoist = []
    shared_subtasks = models.SubTaskShared.query.filter_by(subtask_id=subtask.id).all()
    for shared_subtask in shared_subtasks:
        user_todoist.append((shared_subtask.owner, shared_subtask.todoist_id))
    user_todoist.append((subtask.owner, subtask.todoist_id))
    
    return user_todoist
    

#########################################################################
#                                                                       #
#                               SUBTASKS                                #
#                                                                       #
#########################################################################


def create_subtask(owner: models.User, task_id: int, subtask_name: str, todoist_id: int = None,
                   subtask_desc: str = None,
                   subtask_status: models.TaskStatus = models.TaskStatus.Incomplete,
                   subtask_date: str = None) -> int | bool:
    """
    Creates a subtask under a specified task for the current user in the database.

    Args:
        owner (User): The user creating the subtask. Only the owner of the task can add subtasks.
        task_id (int): The ID of the task to which the subtask belongs.
        subtask_name (str): The name of the subtask (must not be empty or blank).
        subtask_desc (str, optional): A description of the subtask. Defaults to None.
        subtask_status (SubStatus): The status of the subtask (defaults to Incomplete).
        subtask_date (str, optional): The due date for the subtask. Defaults to None.

    Returns:
        int | False: The ID of the subtask if the subtask was successfully created, False otherwise.
    """
    try:
        new_subtask = models.SubTask(owner=owner.id, task_id=task_id, todoist_id=todoist_id,
                                     name=subtask_name, description=subtask_desc,
                                     status=subtask_status, due_date=subtask_date)
        models.db.session.add(new_subtask)
        models.db.session.commit()
        return new_subtask.id
    except Exception as e:
        models.db.session.rollback()
        print(f"Error setting subtask task: {e}")
    return False


def get_subtask_by_id(owner: models.User, id: int, dict=False) -> models.SubTask | dict | None:
    """
    Retrieve a subtask by its database ID.

    :param owner: The owner of the subtask.
    :param id: The database ID of a subtask.
    :param dict: If True, return the subtask as a dictionary. Defaults to False.
    :return SubTask or dict or None: A SubTask instance or a dictionary representation of the subtask
    if dict is True. If no subtask with the given ID exists, None is returned.
    """
    subtask = models.SubTask.query.filter(
        models.SubTask.id == id,
        models.SubTask.owner == owner.id
    ).first()
    if dict and subtask:
        return subtask.to_dict()
    return subtask


def get_subtasks_for_tasks(current_user: models.User, canvas_ids: list[str],
                           format: bool = True) -> list[tuple] | dict:
    """
    Retrieve all subtasks for a series of tasks for the current_user.

    :param current_user: The current user who owns the subtask.
    :type current_user: User
    :param canvas_ids: A list of task IDs to retrieve subtasks for.
    :type canvas_ids: list[str]
    :param format: Return it as a dict of subtasks mapped to each task_id.
    :type format: bool
    :return: A list of tuple with subtasks info.
    :rtype: list[tuple]
    """

    subtasks = models.SubTask.query\
        .join(models.Task, models.SubTask.task_id == models.Task.id).filter(
            models.Task.canvas_id.in_(canvas_ids),
            models.SubTask.owner == current_user.id
        ).with_entities(
            models.SubTask.id,
            models.SubTask.name,
            models.SubTask.description,
            models.SubTask.status,
            models.SubTask.due_date,
            models.Task.canvas_id,
            models.SubTask.todoist_id
        ).all()

    if format:
        subtasks_dict = {}
        for subtask_id, name, description, status, due_date, canvas_id, todoist_id in subtasks:
            subtasks_dict.setdefault(canvas_id, []).append({
                'id': subtask_id,
                'canvas_id': canvas_id,
                'name': name,
                'description': description,
                'status': status.value or 0,
                'due_date': due_date,
                'todoist_id': todoist_id
            })
        return subtasks_dict
    return subtasks


def update_task_or_subtask_status(task: models.Task | models.SubTask,
                                  status: models.TaskStatus) -> bool:
    """
    Change the status of a task or subtask to a new value.

    Args:
        owner (User): The User who owns the task or subtask.
        task (Task | SubTask): The Task or Subtask to
    """
    try:
        task.status = status
        models.db.session.commit()
        return True
    except Exception as e:
        models.db.session.rollback()
        print(f"Error updating task status: {e}")
    return False


def invert_subtask_status(subtask: models.SubTask) -> bool:
    """
    Invert the status of a subtask.

    Args:
        subtask (SubTask): The subtask to invert the status of.

    Returns:
        bool: True if the status was successfully inverted, False otherwise.
    """
    try:
        subtask.status = models.TaskStatus.Incomplete if subtask.status == models.TaskStatus.Completed else models.TaskStatus.Completed
        models.db.session.commit()
        return True
    except Exception as e:
        models.db.session.rollback()
        print(f"Error updating subtask status: {e}")
    return False

#########################################################################
#                                                                       #
#                           CONVERSATION                                #
#                                                                       #
#########################################################################


def create_new_conversation(owner: models.User, canvas_id: int, conv_id: int) -> bool:
    """
    Create a new conversation in the database.

    :param owner: The User who owns the conversation.
    :param canvas_id: The ID of the canvas assignment that the conversation is associated with.
    :param conv_id: The ID of the conversation in the Canvas API.
    :return bool: Returns True if the conversation was created, False otherwise.
    """
    try:
        already_exists = models.Conversation.query.filter_by(owner=owner.id, canvas_id=canvas_id, conversation_id=conv_id).first()
        if already_exists:
            return True
        new_conv = models.Conversation(owner=owner.id, canvas_id=canvas_id, conversation_id=conv_id)
        models.db.session.add(new_conv) 
        models.db.session.commit()
        return True
    except Exception as e:
        models.db.session.rollback()
        print(f"Error creating conversation: {e}")
    return False


def get_user_conversations(owner: models.User, dict: bool=False) -> list[models.Conversation] | list[dict]:
    """
    Retrieve all conversations for a user.

    :param owner: The owner of the conversations.
    :param dict: If True, return the conversations as a list of dictionaries. Defaults to False.
    :return list[Conversation | dict]: A list of all conversations for the user.
    """
    if dict:
        return [conv.to_dict() for conv in models.User.query.get(owner.id).conversations]
    return models.User.query.get(owner.id).conversations


def valid_task_id(owner: models.User, canvas_id: int) -> tuple[int, bool] | None:
    """
    Check if a task ID is valid for a given user to create a conversation.

    :param owner: The owner of the task.
    :param canvas_id: The ID of the canvas assignment to check.
    :return (int, bool): The ID of the canvas assignment if it is valid, and if a conversation already exists for said task.
    """
    task = models.Task.query.filter_by(canvas_id=canvas_id, owner=owner.id).first()
    if not task or not task.canvas_id:
        return None
    conv_exists = models.Conversation.query.filter_by(owner=owner.id, canvas_id=canvas_id).first()
    return canvas_id, True if conv_exists else None


def get_conversation_by_canvas_id(owner: models.User, canvas_id: int) -> list[int]:
    """
    This function retrieves a conversation by the Canvas ID.
    
    :param owner: The owner of the conversation.
    :param canvas_id: The Canvas ID of the conversation.
    :return list[int]: A list of conversations that match the Canvas ID.
    """
    conversations = models.Conversation.query.filter_by(owner=owner.id, canvas_id=canvas_id).all()
    return [conv.conversation_id for conv in conversations]


#########################################################################
#                                                                       #
#                                FILTERS                                #
#                                                                       #
#########################################################################


def get_filters(owner: models.User) -> list[str]:
    """
    Gets all filters for a given user.

    Args:
        owner (User): The User who owns the filters.

    Returns:
        list[str]: A list of filters created by the user.
    """
    filters = models.Filter.query.filter(
        models.Filter.owner == owner.id
    ).with_entities(models.Filter.filter).all()

    filters = [row[0] for row in filters]

    return filters


def create_filter(owner: models.User, filter: str) -> bool:
    """
    Creates a new filter for the given user.

    Args:
        owner (User): The User who will own the filter.
        filter (str): The filter to create.

    Retuns:
        bool: True if the filter was created successfully, False otherwise.
    """
    if filter == '':
        return False

    try:
        filter = models.Filter(owner=owner.id, filter=filter)
        models.db.session.add(filter)
        models.db.session.commit()
        return True
    except sqlalchemy.exc.IntegrityError:
        # This means that a duplicate filter tried to be added.
        # Since it already exists, simply do nothing
        return True
    except Exception as e:
        models.db.session.rollback()
        print(f"Error creating filter: {e}")

    return False


def delete_filter(owner: models.User, filter: str) -> int | None:
    """
    Deletes the given filter owned by the owner.

    Args:
        owner (User): The User that owns the filter.
        filter (str): The filter to delete.

    Returns:
        int | None: The filter's internal ID if one was deleted. If no ID was deleted, None is
        returned instead.

    Raises:
        ValueError: If the given filter does not exist for the given user.
    """
    try:
        filter_db: models.Filter = models.Filter.query.filter(
            models.Filter.owner == owner.id,
            models.Filter.filter == filter
        ).first()

        if filter_db is None:
            raise ValueError

        db_id = filter_db.id

        models.db.session.delete(filter_db)
        models.db.session.commit()

        return db_id
    except ValueError:
        raise ValueError
    except Exception as e:
        models.db.session.rollback()
        print(f"Error deleting filter: {e}")

    return None


#########################################################################
#                                                                       #
#    THIS IS PURELY FOR TESTING DON'T USE THESE FUNCTIONS OTHERWISE     #
#                                                                       #
#########################################################################


def _delete_task_entries() -> None:
    """ATTENTION: Deletes every entry in the Task table."""
    models.Task.query.delete()
    models.db.session.commit()
