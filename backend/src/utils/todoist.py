"""
This file provides utilities for adding tasks to Todoist.
"""


from ctypes import c_bool
from multiprocessing import Manager, Pool
from multiprocessing.managers import ValueProxy
from queue import Queue
from threading import Lock
from time import sleep
from todoist_api_python.api import TodoistAPI


from utils.models import User
from utils.queries import add_or_return_task, set_todoist_task


def add_task_sync(todoist_api_key: str, canvas_task_id: str, task_name: str, class_name: str,
                  due_date: str, owner: User|int):
    """ 
    Synchronously add a task to Todoist.

    :param todoist_api_key: The user's Todoist API key.
    :param canvas_task_id: The ID of the task in Canvas.
    :param task_name: The name of the task to add.
    :param class_name: The name of the class that the assignment is for.
    :param due_date: The date that the assignment is due in YYYY-MM-DD format.
    :param owner: Either the User who will own the task or their ID.
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
    task = add_or_return_task(owner, canvas_task_id)

    # If it doesn't have a Todoist ID associated with it, create a Todoist task
    if not task.todoist_id:
        todoist_task = todoist_api.add_task(
            content=task_name,
            due_string=due_date,
            labels=[class_name]
        )
        set_todoist_task(task, todoist_task.id)


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