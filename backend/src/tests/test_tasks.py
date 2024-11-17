from flask import url_for
import pytest

import utils.canvas as utils_canvas
import utils.queries as queries
import utils.session as session
import utils.todoist as todoist

from .test_courses import fake_login, MockCanvas, MockTodoistAPI

#################################################################
#                                                               #
#                           MOCK DATA                           #
#                                                               #
#################################################################


@pytest.fixture(autouse=True)
def init_test(monkeypatch):
    monkeypatch.setattr(queries, 'Canvas', MockCanvas)
    monkeypatch.setattr(utils_canvas, 'Canvas', MockCanvas)
    monkeypatch.setattr(queries, 'TodoistAPI', MockTodoistAPI)
    monkeypatch.setattr(session, 'decrypt_todoist_key', mock_decrypt_todoist_key)
    monkeypatch.setattr(todoist, 'requests', MockRequests())


def mock_decrypt_todoist_key():
    return 'ttoken'


def mock_get_task_by_canvas_id(current_user, canvas_id, dict=False):
    for task in mock_tasks:
        if task.canvas_id == canvas_id:
            return task

    return None


class MockRequests:
    def post(self, url: str, json={}, data={}, headers=[]):
        match url:
            case 'https://api.todoist.com/rest/v2/tasks':
                return MockResponse(200, {'id': 1})

        if url.startswith('https://api.todoist.com/rest/v2/tasks/'):
            return MockResponse(200, {})

        raise ValueError


class MockResponse:
    def __init__(self, status_code: int, data: dict):
        self.status_code = status_code
        self.data = data
        self.ok = status_code == 200

    def json(self):
        return self.data


class MockTask:
    def __init__(self, owner, id, canvas_id, todoist_id, description=''):
        self.owner = owner
        self.id = id
        self.canvas_id = canvas_id
        self.todoist_id = todoist_id
        self.description = description


mock_tasks = [
    MockTask(1, '1', 'a', 'i', 'desc'),
    MockTask(1, '2', 'b', 'ii'),
    MockTask(1, '3', 'c', 'iii'),
]


#################################################################
#                                                               #
#                           UNIT TESTS                          #
#                                                               #
#################################################################


def test_add_task(client):
    # Check that an unauthenticated user can't add tasks
    resp = client.post(url_for('api_v1.tasks.add_task_user'), json={'name': 'hi',
                                                                    'due_at': '2000-01-01T12:00'})
    assert resp.status_code == 401
    assert resp.json is None

    fake_login(client)

    # Check that an authorized user can add tasks
    resp = client.post(url_for('api_v1.tasks.add_task_user'), json={'name': 'hi',
                                                                    'due_at': '2000-01-01T12:00'})
    assert resp.status_code == 200
    assert type(resp.json) is dict
    assert resp.json['success'] is True


def test_add_subtask(client, monkeypatch):
    monkeypatch.setattr(queries, 'get_task_by_canvas_id', mock_get_task_by_canvas_id)

    subtask = {
        'canvas_id': 'a',
        'name': 'subtask',
        'description': 'desc',
        'status': 0,
        'due_date': '2000-01-01T12:00'
    }

    # Check than an unauthenticated user can't add subtasks
    resp = client.post(url_for('api_v1.tasks.add_subtask_user'), json=subtask)
    assert resp.status_code == 401
    assert resp.json is None

    fake_login(client)
    resp = client.post(url_for('api_v1.tasks.add_task_user'), json={'name': 'hi',
                                                                    'due_at': '2000-01-01T12:00'})

    # Check that an authorized user can add subtasks
    resp = client.post(url_for('api_v1.tasks.add_subtask_user'), json=subtask)
    assert resp.status_code == 200
    assert type(resp.json) is dict
    assert resp.json['id'] == 1
    assert resp.json['success'] is True
