import os
import pytest


import api.v1.courses as courses_api


def _has_canvas_api_token() -> bool:
    # Try to get the location of the Canvas API key as an environment variable
    canvas_api_path = os.environ.get('CANVAS_API_TOKEN', '../../secrets/canvas_api_token.txt')

    return os.path.isfile(canvas_api_path)


def _load_canvas_api_token() -> str:
    with open(os.environ.get('CANVAS_API_TOKEN', '../../secrets/canvas_api_token.txt')) as f:
        return f.readline().strip()


def _has_todoist_api_token() -> bool:
    # Try to get the location of the Todoist API key as an environment variable
    todoist_api_path = os.environ.get('TODOIST_API_TOKEN', '../../secrets/todoist_api_token.txt')

    return os.path.isfile(todoist_api_path)


def _load_todoist_api_token() -> str:
    with open(os.environ.get('TODOIST_API_TOKEN', '../../secrets/todoist_api_token.txt')) as f:
        return f.readline().strip()


@pytest.mark.skipif(not _has_canvas_api_token(), reason='Missing Canvas API token')
def test_get_all_courses():
    canvas_token = _load_canvas_api_token()

    # Get all active courses
    courses = courses_api.get_all_courses(canvas_token)
    
    # Assume that one of the current active class is ITSC 4155, which will be true this semester
    # ITSC 4155 has a Canvas ID of 222949
    try:
        itsc_4155 = next(filter(lambda x: x['id'] == 222949, courses))
    except:
        pytest.fail("ITSC 4155 does not exist in Canvas response.")


@pytest.mark.skipif(not _has_canvas_api_token(), reason='Missing Canvas API token')
def test_get_course():
    assert False


@pytest.mark.skipif(not _has_canvas_api_token(), reason='Missing Canvas API token')
def test_get_course_assignments():
    assert False


@pytest.mark.skipif(not _has_canvas_api_token(), reason='Missing Canvas API token')
def test_get_course_assignment():
    assert False
