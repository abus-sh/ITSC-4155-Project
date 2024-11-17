"""
A series of tests for updating the descriptions of tasks.
"""

from flask import url_for
import pytest

import utils.queries as queries
import utils.session as session
import utils.todoist as todoist

from .test_courses import fake_login, MockCanvas, MockTodoistAPI
from .test_tasks import mock_decrypt_todoist_key, MockRequests, mock_tasks,\
mock_get_task_by_canvas_id

#################################################################
#                                                               #
#                           MOCK DATA                           #
#                                                               #
#################################################################


@pytest.fixture(autouse=True)
def init_test(monkeypatch):
    # Need to set TODOIST_SECRET before importing to ensure that it can read a fake Todoist secret
    monkeypatch.setenv('TODOIST_SECRET', 'secrets.example/todoist_secret.txt')


@pytest.fixture(autouse=True)
def init_test(monkeypatch):
    monkeypatch.setattr(queries, 'Canvas', MockCanvas)
    monkeypatch.setattr(queries, 'TodoistAPI', MockTodoistAPI)
    monkeypatch.setattr(queries, 'get_task_by_id', mock_get_task_by_id)
    monkeypatch.setattr(queries, 'get_task_by_canvas_id', mock_get_task_by_canvas_id)
    monkeypatch.setattr(session, 'decrypt_todoist_key', mock_decrypt_todoist_key)
    monkeypatch.setattr(todoist, 'requests', MockRequests())


def mock_get_task_by_id(owner, id, dict=False):
    for task in mock_tasks:
        if task.id == id:
            return task

    return None


#################################################################
#                                                               #
#                           UNIT TESTS                          #
#                                                               #
#################################################################


def test_no_auth(client):
    # Test that an unauthenticated user can't update a task's description
    resp = client.patch(url_for('api_v1.tasks.update_description', task_id='1'), json={
        'description': 'new desc',
        'task_type': 'native'
    })

    # Check the response
    assert resp.status_code == 401
    assert resp.json is None

    # Check that the task wasn't changed
    updated_task = filter(lambda x: x.id == '1', mock_tasks)
    updated_task = next(updated_task, None)
    assert updated_task is not None
    assert updated_task.id == '1'
    assert updated_task.description == 'desc'


def test_404(client):
    fake_login(client)

    # Test a non-existent task
    resp = client.patch(url_for('api_v1.tasks.update_description', task_id='100'), json={
        'description': 'new desc',
        'task_type': 'native'
    })

    # Check the reponse
    assert resp.status_code == 404
    assert resp.json is not None
    assert 'success' in resp.json
    assert not resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'No task with the given ID exists.'

    # Check that the task wasn't changed
    updated_task = filter(lambda x: x.id == '1', mock_tasks)
    updated_task = next(updated_task, None)
    assert updated_task is not None
    assert updated_task.id == '1'
    assert updated_task.description == 'desc'


def test_missing_desc(client):
    fake_login(client)

    # Test missing desc
    resp = client.patch(url_for('api_v1.tasks.update_description', task_id='1'), json={
        'task_type': 'native'
    })

    # Check that the response is OK
    assert resp.status_code == 400
    assert resp.json is not None
    assert 'success' in resp.json
    assert not resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'No description provided.'

    # Check that the task wasn't changed
    updated_task = filter(lambda x: x.id == '1', mock_tasks)
    updated_task = next(updated_task, None)
    assert updated_task is not None
    assert updated_task.id == '1'
    assert updated_task.description == 'desc'


def test_long_desc(client):
    fake_login(client)

    # Test too long desc
    resp = client.patch(url_for('api_v1.tasks.update_description', task_id='1'), json={
        'description': 'a'*501,
        'task_type': 'native'
    })

    # Check that the response is OK
    assert resp.status_code == 400
    assert resp.json is not None
    assert 'success' in resp.json
    assert not resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'Description is too long.'

    # Check that the task wasn't changed
    updated_task = filter(lambda x: x.id == '1', mock_tasks)
    updated_task = next(updated_task, None)
    assert updated_task is not None
    assert updated_task.id == '1'
    assert updated_task.description == 'desc'


def test_bad_desc(client):
    fake_login(client)

    # Test wrong type for desc
    resp = client.patch(url_for('api_v1.tasks.update_description', task_id='1'), json={
        'description': 1,
        'task_type': 'native'
    })

    # Check that the response is OK
    assert resp.status_code == 400
    assert resp.json is not None
    assert 'success' in resp.json
    assert not resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'Invalid description.'

    # Check that the task wasn't changed
    updated_task = filter(lambda x: x.id == '1', mock_tasks)
    updated_task = next(updated_task, None)
    assert updated_task is not None
    assert updated_task.id == '1'
    assert updated_task.description == 'desc'


def test_bad_task_type(client):
    fake_login(client)

    # Test wrong value for task type
    resp = client.patch(url_for('api_v1.tasks.update_description', task_id='1'), json={
        'description': 'new desc',
        'task_type': 'fake_type'
    })

    # Check that the response is OK
    assert resp.status_code == 400
    assert resp.json is not None
    assert 'success' in resp.json
    assert not resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'Invalide task_type.'

    # Check that the task wasn't changed
    updated_task = filter(lambda x: x.id == '1', mock_tasks)
    updated_task = next(updated_task, None)
    assert updated_task is not None
    assert updated_task.id == '1'
    assert updated_task.description == 'desc'


def test_default_task_type(client):
    fake_login(client)

    # Test default task type
    resp = client.patch(url_for('api_v1.tasks.update_description', task_id='a'), json={
        'description': 'new desc'
    })

    # Check that the response is OK
    assert resp.status_code == 200
    assert resp.json is not None
    assert 'success' in resp.json
    assert resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'OK.'

    # Check that the value actually changed
    updated_task = filter(lambda x: x.canvas_id == 'a', mock_tasks)
    updated_task = next(updated_task, None)
    assert updated_task is not None
    assert updated_task.canvas_id == 'a'
    assert updated_task.description == 'new desc'


def test_canvas_task_type(client):
    fake_login(client)

    # Test Canvas task type
    resp = client.patch(url_for('api_v1.tasks.update_description', task_id='a'), json={
        'description': 'new desc',
        'task_type': 'canvas'
    })

    # Check that the response is OK
    assert resp.status_code == 200
    assert resp.json is not None
    assert 'success' in resp.json
    assert resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'OK.'

    # Check that the value actually changed
    updated_task = filter(lambda x: x.canvas_id == 'a', mock_tasks)
    updated_task = next(updated_task, None)
    assert updated_task is not None
    assert updated_task.canvas_id == 'a'
    assert updated_task.description == 'new desc'


def test_native_task_type(client):
    fake_login(client)

    # Task valid task with native ID
    resp = client.patch(url_for('api_v1.tasks.update_description', task_id='1'), json={
        'description': 'new desc',
        'task_type': 'native'
    })

    # Check that the response is OK
    assert resp.status_code == 200
    assert resp.json is not None
    assert 'success' in resp.json
    assert resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'OK.'

    # Check that the value actually changed
    updated_task = filter(lambda x: x.id == '1', mock_tasks)
    updated_task = next(updated_task, None)
    assert updated_task is not None
    assert updated_task.id == '1'
    assert updated_task.description == 'new desc'
