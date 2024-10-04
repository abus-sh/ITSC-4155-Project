import os
import pytest


import api.v1.courses as courses_api


def _has_canvas_api_token() -> bool:
    # Try to get the location of the Canvas API key as an environment variable
    canvas_api_path = os.environ.get('CANVAS_API_TOKEN', '../../secrets/canvas_api_token.txt')

    return os.path.isfile(canvas_api_path)


def _has_todoist_api_token() -> bool:
    # Try to get the location of the Todoist API key as an environment variable
    todoist_api_path = os.environ.get('TODOIST_API_TOKEN', '../../secrets/todoist_api_token.txt')

    return os.path.isfile(todoist_api_path)


@pytest.mark.skipif(not _has_canvas_api_token(), reason='Missing Canvas API token')
def test_get_all_courses():
    assert False


@pytest.mark.skipif(not _has_canvas_api_token(), reason='Missing Canvas API token')
def test_get_course():
    assert False


@pytest.mark.skipif(not _has_canvas_api_token(), reason='Missing Canvas API token')
def test_get_course_assignments():
    assert False


@pytest.mark.skipif(not _has_canvas_api_token(), reason='Missing Canvas API token')
def test_get_course_assignment():
    assert False
