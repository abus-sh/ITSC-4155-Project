import os, time
from contextlib import contextmanager


@contextmanager
def time_it(info: str, end_text: str=' seconds'):
    """Time the time it takes for the `with` block to execute fully in seconds"""
    start_time = time.time()
    yield
    end_time = time.time()
    print(f"{info} {end_time - start_time:.4f}{end_text}")


def get_canvas_url() -> str:
    """
    Returns the base URL for Canvas to make API calls against.

    :return str: The base URL for Canvas.
    """
    return os.environ.get('CANVAS_BASE_URL', 'https://uncc.instructure.com')