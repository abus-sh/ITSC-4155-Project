"""
This file provides utilities for adding tasks to Todoist.
"""


from datetime import datetime
from todoist_api_python.api import TodoistAPI
import gevent, requests, uuid, json

from api.v1.courses import get_all_courses, get_course_assignments
from utils.models import User, TaskStatus, Task, SubTask
from utils.settings import localize_date, date_passed, time_it, is_valid_date
from utils.queries import add_or_return_task, update_task_id, set_task_duedate, \
    get_task_by_canvas_id, create_subtask, get_task_or_subtask_by_todoist_id,\
    update_task_or_subtask_status


def add_update_tasks(user_id: int, canvas_key: str, todoist_key: str):
    """
    Add all missing tasks for a given user or update them if the due date has changed.

    :param user_id: The primary key for the current user.
    :param canvas_key: The Canvas API key for the current user.
    :param todoist_key: The Todoist API key for the current user.
    """
    
    # Get all courses from canvas
    with time_it("      Canvas requests: "):
        courses = get_all_courses(canvas_key)

        greenlets = [gevent.spawn(get_course_assignments, course['id'], canvas_key) for course in courses]
        gevent.joinall(greenlets)
        
    # Creates list of all assignments
    with time_it("      Create assignments list: "):
        all_assignments = [assignment for greenlet in greenlets for assignment in greenlet.value]
        # I may have a better alternative for the sorting
        all_assignments.sort(key=_get_assignment_date_or_default)
    
    todoist_queue = []  # Command queue to send to todoist
    temp_ids = {}       # temp id mapping (for updating the todoist_id after sending the request to todoist)
    
    todoist_url = 'https://api.todoist.com/sync/v9/sync'
    headers = {"Authorization": f"Bearer {todoist_key}"}

    with time_it("      Creating Tasks: "):
        for assignment in all_assignments:
            # Only consider assignments where due date has not already passed
            due_date_str = assignment.get('due_at')
            if due_date_str:
                date_aware = localize_date(datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M:%SZ'))

            if not date_passed(date_aware):
                due_date = date_aware.strftime('%Y-%m-%d %H:%M:%S')
                # Creates tasks in the database if they dont exist / update them, and creates the todoist queue
                add_tasks_to_database(assignment, due_date, user_id, todoist_queue, temp_ids)

    # If the todoist queue is not empty (something need to be added/updated)
    if todoist_queue:
        body = {
            'sync_token': '*',
            'commands': json.dumps(todoist_queue), # Todoist command queue
        }
        # Send the todoist queue request
        response_data = send_post_todoist(todoist_url, body, headers)
        
        # Update the tasks in the database with their final todoist_id
        with time_it("      Updating IDs of assignments: "):
            temp_id_mapping = response_data.get('temp_id_mapping')
            if temp_id_mapping:
                for temp_id, final_id in temp_id_mapping.items():
                    task_id = temp_ids[temp_id]
                    update_task_id(task_id, final_id)


def add_tasks_to_database(assignment: dict, due_date: str, owner: User|int, todoist_queue: list, temp_ids: dict):
    """
    Adds tasks to the database and prepares them for synchronization with Todoist.

    Args:
        assignment (dict): A dictionary containing assignment details, including 'id' and 'name'.
        due_date (str): The due date for the task in string format.
        owner (User | int): The owner of the task, which can be a User object or an integer user ID.
        todoist_queue (list): A list that stores tasks to be added or updated in Todoist.
        temp_ids (dict): A dictionary mapping temporary task IDs to their corresponding database IDs.

    Returns:
        None
    """
    if type(owner) == User:
        owner = owner.id

    # Debug info, remove later
    if type(owner) != int:
        print(f"Owner is {owner}, type is {type(owner)}")
    
    temp_id = str(uuid.uuid4())     # Todoist wants a unique uuid for every command
    
    # Get task from database or add it if it doesnt exists
    task = add_or_return_task(owner, assignment['id'], due_date=due_date)
    
    # If the task doesn't have a todoist it, create the command for adding it to todoist
    if not task.todoist_id:
        add_task_todoist = {
            "type": "item_add",
            "temp_id": temp_id,
            "uuid": str(uuid.uuid4()), 
            "args": {
                "content": assignment['name'],
                "due": {"date": due_date},
                "labels": ["assignment"]
            }
        }
        # Put the command in the queue that will be sent to Todoist 
        todoist_queue.append(add_task_todoist)
        # Save the temp id of the task, this will be used to get the final todoist_id after sending the request
        temp_ids.update({temp_id: task.id})
    
    # If the task exists but the due date has been updated, create the command for updating it in todoist
    elif task.todoist_id and task.due_date != due_date:
        update_task_todoist = {
            "type": "item_update",
            "uuid": str(uuid.uuid4()), 
            "args": {
                "id": task.todoist_id,
                "due": {"date": due_date},
            }
        }
        # Put the command in the queue that will be sent to Todoist
        todoist_queue.append(update_task_todoist)
        # Update the task due date in the database
        set_task_duedate(task, due_date)


def add_subtask(current_user: User, todoist_key: str, canvas_id: str, subtask_name: str, subtask_desc: str=None, 
                   subtask_status: TaskStatus=TaskStatus.Incomplete, subtask_date: str=None) -> int|bool:
    """
    Creates a subtask under a specified task for the current user in both todoist and the database.

    Args:
        current_user (User): The user creating the subtask. Only the owner of the task can add subtasks.
        todoist_key (str): The Todoist API key for the current user.
        canvas_id (str): The ID of the canvas assignment to which the task of the subtask belongs.
        subtask_name (str): The name of the subtask (must not be empty or blank).
        subtask_desc (str, optional): A description of the subtask. Defaults to None.
        subtask_status (SubStatus): The status of the subtask (defaults to Incomplete).
        subtask_date (str, optional): The due date for the subtask. Defaults to None.

    Returns:
        int|False: The ID of the subtask if the subtask was successfully created, False otherwise.
    """
    # Check that the subtask belogs to a valid assignment that belong to the current user
    task = get_task_by_canvas_id(current_user, canvas_id, dict=False)

    if task and task.owner == current_user.id and subtask_name.strip() != '':
        try:
            # Get due date in valid string format
            due_date = is_valid_date(subtask_date)
            if not due_date:
                print("Error")
                return False

            header = {
                "Authorization": f"Bearer {todoist_key}",
                "Content-Type": "application/json"
                }
            body = {
                "content": subtask_name,
                "description": subtask_desc,
                "due_date": due_date,
                "parent_id": task.todoist_id,
            }
            
            # Create subtask and receive the todoist id
            response_data = send_post_todoist("https://api.todoist.com/rest/v2/tasks", json.dumps(body), header)
            if response_data:
                todoist_id = response_data.get('id', None)
                if not todoist_id:
                    return False
                
                # If subtask is already marked as complete, close it
                if subtask_status == TaskStatus.Completed:
                    response = requests.post(f"https://api.todoist.com/rest/v2/tasks/{todoist_id}/close", headers={"Authorization": f"Bearer {todoist_key}"})
                    if response.status_code != 204: # Failure to mark subtask as complete
                        subtask_status = TaskStatus.Incomplete
                
                # Create subtask in database
                new_subtask_id = create_subtask(current_user, task.id, subtask_name, todoist_id, subtask_desc,
                                             subtask_status, due_date)
                return new_subtask_id
        except Exception as e:
            print(e)
    return False


def close_task(current_user: User, todoist_key: str, todoist_task_id: str) -> bool:
    """
    Marks a task or subtask as complete for the current user.

    Args:
        current_user (User): The user that owns the task or subtask.
        todoist_key (str): The Todoist API key for the current user.
        todoist_task_id (str): The ID of the task or subtask in Todoist.
    
    Returns:
        bool: True if the task or subtask was completed, False otherwise.
    """
    # Get the task in the database
    task: Task|SubTask|None = get_task_or_subtask_by_todoist_id(current_user, todoist_task_id)
    if task == None:
        return False

    # Mark task as complete in Todoist
    response = requests.post(f"https://api.todoist.com/rest/v2/tasks/{todoist_task_id}/close",\
                             headers={"Authorization": f"Bearer {todoist_key}"})
    
    # Per documation, 204 indicates success
    if response.status_code == 204:
        # Complete task in database
        update_task_or_subtask_status(current_user, task, TaskStatus.Completed)

        return True

    return False


def open_task(current_user: User, todoist_key: str, todoist_task_id: str) -> bool:
    """
    Marks a task or subtask as in progress for the current user.

    Args:
        current_user (User): The user that owns the task or subtask.
        todoist_key (str): The Todoist API key for the current user.
        todoist_task_id (str): The ID of the task or subtask in Todoist.
    
    Returns:
        bool: True if the task or subtask was marked as in progress, False otherwise.
    """

    # Get the task in the database
    task: Task|SubTask|None = get_task_or_subtask_by_todoist_id(current_user, todoist_task_id)
    if task == None:
        return False
    
    # Mark task as in progress in Todoist
    response = requests.post(f"https://api.todoist.com/rest/v2/tasks/{todoist_task_id}/reopen",\
                             headers={"Authorization": f"Bearer {todoist_key}"})
    if response.status_code == 204:
        update_task_or_subtask_status(current_user, task, TaskStatus.Incomplete)

        return True
    
    return False


def toggle_task(current_user: User, todoist_key: str, todoist_task_id: str) -> bool:
    """
    Toggles a task's or subtask's status for the current user.

    Args:
        current_user (User): The user that owns the task or subtask.
        todoist_key (str): The Todoist API key for the current user.
        todoist_task_id (str): The ID of the task or subtask in Todoist.
    
    Returns:
        bool: True if the task's or subtask's status was toggled, False otherwise.
    """
    # Get the task in the database
    task: Task|SubTask|None = get_task_or_subtask_by_todoist_id(current_user, todoist_task_id)
    if task == None:
        return False
    
    # Handle each enum seperately in case more states happen in the future
    if task.status == TaskStatus.Completed:
        return open_task(current_user, todoist_key, todoist_task_id)
    elif task.status == TaskStatus.Incomplete:
        return close_task(current_user, todoist_key, todoist_task_id)
    
    return False


def send_post_todoist(todoist_url, body, headers):
    """
    Sends a POST request to the Todoist API.

    Args:
        todoist_url (str): The URL endpoint of the Todoist API.
        body (dict): The data to be sent in the request body, typically as a dictionary.
        headers (dict): The headers to include in the request: the authorization token.

    Returns:
        dict: The JSON response data from the Todoist API if the request is successful. If not, raise an exception.
    """
    with time_it("      Send Todoist request: "):
        response = requests.post(todoist_url, data=body, headers=headers)
    response_data = response.json()
    if not response.ok:
        error = response_data.get('error') 
        print(response.text)
        print("Error sending to Todoist: ", error)
        raise Exception
    return response_data # Return response json data


def _get_assignment_date_or_default(assignment: dict, default:str='~') -> str:
    """
    Get the due date of an assignment. If the due date is None, return a default value instead.

    :param assignment: The assignment to extract the date from.
    :param default: The string to return if the assignment's due date is None.
    :return str: The due date of the assignment or the default value.
    """
    due_date = assignment['due_at']
    if due_date:
        return due_date
    else:
        return default
