"""
This file provides utilities for adding tasks to Todoist.
"""


from ctypes import c_bool
from datetime import datetime, timedelta
from multiprocessing import Manager, Pool
from multiprocessing.managers import ValueProxy
from queue import Queue
from threading import Lock
from time import sleep
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
    task = add_or_return_task(owner, canvas_task_id, due_date)

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


# TODO: this breaks in very strange ways. Ex. sometimes functions will stop executing if specific
# attributes are accessed on a variable. I suspect this is related to some really screwy stuff with
# pointers, but I'm not sure. This is probably impossible to do in a reasonable amount of time
# without using something like Celery w/ Redis.
class FuncQueue():
    """
    A queue of functions that will be asynchronously executed by processes.
    """

    FUNC_IDS = dict([
        ('ADD_TASK', add_task_sync)
    ])

    def __init__(self, num_processes: int=3):
        """
        Initialize a FuncQueue.

        :param num_processes: The number of processes to create. Defaults to 3 if not specified.
        """

        # This is currently broken, don't allow it to be contstructed.
        raise ValueError

        self._pool = Pool(processes=num_processes)
        self._manager = Manager()
        self._queue_lock = self._manager.Lock()
        self._queue = self._manager.Queue()
        self._should_run = self._manager.Value(c_bool, True)
        
        self._workers = [
            self._pool.apply_async(FuncQueue._worker,
                                   (self._queue_lock, self._queue, self._should_run))
            for _ in range(num_processes)
        ]


    def add_func(self, func_id: str, *args, **kwargs) -> bool:
        """
        Add a function to the queue to execute. This will block until the StoredFunc can be added.
        Functions will not be added if `graceful_shutdown` has been called.

        :param func_id: The ID of the function to call. Must be a valid key in FuncQueue.FUNC_IDS.
        :param *args: The positional arguments to func.
        :param **kwargs: The named arguments to func.
        :return bool: Whether the function was added. Returns False if a shutdown has been
        initiated.
        :raises ValueError: If func_id is not a valid key in FuncQueue.FUNC_IDS.
        """
        # Validate that func_id is a valid ID
        if func_id not in FuncQueue.FUNC_IDS:
            raise ValueError

        # Don't accept jobs if the queue should be shutting down
        if not self._should_run.get():
            return False
        
        # Add the job to the queue
        with self._queue_lock:
            self._queue.put((func_id, args, kwargs))

        return True


    def graceful_shutdown(self):
        """
        Begin a graceful shutdown of the queue. All functions currently in the queue will be
        finished before exiting, but no new functions will be accepted.
        """
        self._should_run.set(False)
    

    def wait(self):
        """
        Begin a graceful shutdown and wait for all functinos in the queue to finish. Blocks until
        all functions are finished.
        """
        self.graceful_shutdown()
        [w.wait() for w in self._workers]
    

    def add_task_queued(self, todoist_api_key, canvas_task_id: str, task_name: str, class_name: str,
                        due_date: str, owner: User|int):
        """
        Queue a task to be added asynchronously.

        :param todoist_api_key: The user's Todoist API key.
        :param canvas_task_id: The ID of the task in Canvas.
        :param task_name: The name of the task to add.
        :param class_name: The name of the class that the assignment is for.
        :param due_date: The date that the assignment is due in YYYY-MM-DD format.
        :param owner: Either the User who will own the task or their ID.
        """
        self.add_func(
            'ADD_TASK',
            todoist_api_key, canvas_task_id, task_name, class_name, due_date, owner
        )


    @staticmethod
    def _worker(queue_lock: Lock, queue: Queue,
           should_run: ValueProxy[bool]):
            while True:
                # Lock the queue to prevent multiple threads from trying to get items at the same time
                queue_lock.acquire()

                # If no items are availble...
                if queue.empty():
                    # Immediately release the queue lock, it won't be used
                    queue_lock.release()

                    # If the worker shouldn't be running, end it
                    if not should_run.get():
                        return

                    # If it should still be running, wait 1 second for a new item
                    sleep(1)
                    continue
                # If items are available...
                else:
                    # Get the func information and release the lock
                    func_id, args, kwargs = queue.get()
                    queue_lock.release()

                    # Convert the function id to a function and execute it
                    func = FuncQueue.FUNC_IDS[func_id]
                    print(f"Got {func_id} -> {func}")
                    print(f"args: {args}, kwargs: {kwargs}")
                    func(*args, **kwargs)
    


    # TODO: see if custom registerable methods will screw anything up. Also test if lambda/local
    # functions are still broken w/ this method.

#todoist_queue = FuncQueue()