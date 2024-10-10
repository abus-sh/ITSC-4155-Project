"""
This file provides utilities for adding tasks to Todoist.
"""


from datetime import datetime, timedelta
from todoist_api_python.api import TodoistAPI
import gevent


from api.v1.courses import get_all_courses, get_course_assignments
from utils.models import User
from utils.queries import add_or_return_task, set_todoist_task, update_task_duedate


def add_missing_tasks(user_id: int, canvas_key: str, todoist_key: str):
    """
    Add all missing tasks for a given user.

    :param user_id: The primary key for the current user.
    :param canvas_key: The Canvas API key for the current user.
    :param todoist_key: The Todoist API key for the current user.
    """
    courses = get_all_courses(canvas_key)

    # Don't spam the Todoist API, set rates limits. Only add 25 tasks per logon.
    rate_limit = 25
    counter = 0

    greenlets = [gevent.spawn(get_course_assignments, course['id'], canvas_key) for course in courses]
    gevent.joinall(greenlets)
    all_courses_assignments = [greenlet.value for greenlet in greenlets]

    # Account for timezone, UNCC is in (GMT-4)
    timezone_gmt = timedelta(hours=4)
    for course_assignments in all_courses_assignments:
        course_assignments.sort(key=_get_assignment_date_or_default)
        
        for assignment in course_assignments:
            try:
                due_date = assignment['due_at']
                due_date = datetime.strptime(due_date, '%Y-%m-%dT%H:%M:%SZ') - timezone_gmt
            except:
                due_date = datetime.now()

            # Don't add Todoist tasks for assignments that are in the past.
            now = datetime.now()
            if due_date > now:
                due_date = due_date.strftime('%Y-%m-%d')
                api_queried = add_task_sync(todoist_key, assignment['id'], assignment['name'],
                                            'automated', due_date, user_id)
                if api_queried:
                    counter += 1
                    if counter >= rate_limit:
                        return


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


def add_task_sync(todoist_api_key: str, canvas_task_id: str, task_name: str, class_name: str,
                  due_date: str, owner: User|int) -> bool:
    """ 
    Synchronously add a task to Todoist.

    :param todoist_api_key: The user's Todoist API key.
    :param canvas_task_id: The ID of the task in Canvas.
    :param task_name: The name of the task to add.
    :param class_name: The name of the class that the assignment is for.
    :param due_date: The date that the assignment is due in YYYY-MM-DD format.
    :param owner: Either the User who will own the task or their ID.
    :return bool: Returns True if the Todoist API was queried, False otherwise.
    """
    if type(owner) == User:
        owner = owner.id

    # Debug info, remove later
    if type(owner) != int:
        print(f"Owner is {owner}, type is {type(owner)}")
    
    # Standardize class_name
    class_name = class_name.upper().replace(" ", "")

    todoist_api = TodoistAPI(todoist_api_key)

    # Add the task if it doesn't exist or get it if it does
    task = add_or_return_task(owner, canvas_task_id, due_date=due_date)

    # If it doesn't have a Todoist ID associated with it, create a Todoist task
    if not task.todoist_id:
        todoist_task = todoist_api.add_task(
            content=task_name,
            due_string=due_date,
            labels=[class_name]
        )
        set_todoist_task(task, todoist_task.id)
        return True
    # Task already associated with a Todoist id, but due date was changed. 
    # Update the due_date in database and todoist.
    elif task.todoist_id and task.due_date != due_date:
        if todoist_api.update_task(task.todoist_id, due_string=due_date):
            update_task_duedate(task, due_date)
            return True
    return False 
