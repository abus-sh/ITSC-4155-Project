import os


def get_canvas_url() -> str:
    """
    Returns the base URL for Canvas to make API calls against.

    :return str: The base URL for Canvas.
    """
    return os.environ.get('CANVAS_BASE_URL', 'https://uncc.instructure.com')