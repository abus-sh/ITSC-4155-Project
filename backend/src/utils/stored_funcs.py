"""
Provides a method to queue functions to execute asynchronously via an arbitrary number of worker
threads.
"""


from ctypes import c_bool
from multiprocessing import Manager, Pool
from multiprocessing.managers import ValueProxy
from queue import Queue
from time import sleep
from threading import Lock
from typing import Callable


class StoredFunc():
    """
    A representation of a function with arguments to call later. To create a StoredFunc to execute
    `f(1, 2, foo=bar)`, create `func = StoredFunc(f, 1, 2, foo=bar)`. A StoredFunc can be executed
    by calling it (ex. `func()`).

    :param func: The function to call later.
    :type func: Callable
    :param *args: The positional arguments to func.
    :type *args: tuple
    :param **kwargs: The named arguments to func.
    :type **kwargs: dict[str, any]
    """
    _func: Callable
    _args: tuple
    _kwargs: dict[str, any]


    def __init__(self, func: Callable, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs


    def __call__(self):
        self._func(*self._args, **self._kwargs)


class FuncQueue():
    """
    A queue of functions that will be asynchronously executed by processes.
    """

    def __init__(self, num_processes: int=3):
        """
        Initialize a FuncQueue.

        :param num_processes: The number of processes to create. Defaults to 3 if not specified.
        """
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


    def add_func(self, func: Callable, *args, **kwargs) -> bool:
        """
        Add a function to the queue to execute. This will block until the StoredFunc can be added.
        Functions will not be added if `graceful_shutdown` has been called.

        :param func: The name of the function to call.
        :param *args: The positional arguments to func.
        :param **kwargs: The named arguments to func.
        :return bool: Whether the function was added. Returns False if a shutdown has been
        initiated.
        """
        if not self._should_run.get():
            return False

        func = StoredFunc(func, *args, **kwargs)
        with self._queue_lock:
            self._queue.put(func)
        
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
                    # Get the func, release the lock, and execute it
                    func = queue.get()
                    queue_lock.release()
                    func()
