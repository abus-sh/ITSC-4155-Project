"""
A series of tests for getting, creating, and deleting filters.
"""

from flask import url_for
import pytest

import utils.queries as queries

from .test_courses import fake_login, MockCanvas, MockTodoistAPI

#################################################################
#                                                               #
#                           MOCK DATA                           #
#                                                               #
#################################################################


@pytest.fixture(autouse=True)
def init_test(monkeypatch):
    # Initialize consistent test data
    global mock_filters
    mock_filters = [
        'abc',
        '123',
        'testing'
    ]

    monkeypatch.setattr(queries, 'get_filters', mock_get_filters)
    monkeypatch.setattr(queries, 'create_filter', mock_create_filter)
    monkeypatch.setattr(queries, 'delete_filter', mock_delete_filter)

    monkeypatch.setenv('TODOIST_SECRET', 'secrets.example/todoist_secret.txt')
    monkeypatch.setattr(queries, 'Canvas', MockCanvas)
    monkeypatch.setattr(queries, 'TodoistAPI', MockTodoistAPI)


def mock_get_filters(owner):
    return mock_filters


def mock_create_filter(owner, filter):
    if filter == '':
        return False
    
    if filter not in mock_filters:
        mock_filters.append(filter)

    return True


def mock_delete_filter(owner, filter):
    if filter not in mock_filters:
        raise ValueError
    
    for i, f in enumerate(mock_filters):
        if f == filter:
            mock_filters.remove(filter)
            return i
    
    return None


#################################################################
#                                                               #
#                           UNIT TESTS                          #
#                                                               #
#################################################################


def test_get_no_auth(client):
    # Test that an unauthenticated user can't access filters
    resp = client.get(url_for('api_v1.filters.get_filters'))

    # Check the response
    assert resp.status_code == 401
    assert resp.json is None


def test_get_auth(client):
    fake_login(client)

    # Test that an authenticated user can access filters
    resp = client.get(url_for('api_v1.filters.get_filters'))

    # Check the response
    assert resp.status_code == 200
    assert resp.json is not None
    assert 'filters' in resp.json
    assert type(resp.json['filters']) is list
    assert len(resp.json['filters']) == 3
    assert resp.json['filters'] == ['abc', '123', 'testing']


def test_post_no_auth(client):
    # Test that an unauthenticated user can't create filters
    resp = client.post(url_for('api_v1.filters.create_filter'), json={
        'filter': 'newfilter'
    })

    # Check the response
    assert resp.status_code == 401
    assert resp.json is None

    # Check that no changes were made
    assert 'newfilter' not in mock_filters


def test_post_missing(client):
    fake_login(client)

    # Test that a filter won't be created if one isn't specified
    resp = client.post(url_for('api_v1.filters.create_filter'), json={})
    
    # Check the response
    assert resp.status_code == 400
    assert resp.json is not None
    assert 'success' in resp.json
    assert not resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'Missing or invalid filter.'

    # Check that no filter was created
    assert len(mock_filters) == 3


def test_post_invalid(client):
    fake_login(client)

    # Test that a filter won't be created if an invalid one is specified
    resp = client.post(url_for('api_v1.filters.create_filter'), json={
        'filter': 1
    })
    
    # Check the response
    assert resp.status_code == 400
    assert resp.json is not None
    assert 'success' in resp.json
    assert not resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'Missing or invalid filter.'

    # Check that no filter was created
    assert len(mock_filters) == 3


def test_post_auth(client):
    fake_login(client)

    # Test that an authenticated user can create filters
    resp = client.post(url_for('api_v1.filters.create_filter'), json={
        'filter': 'newfilter'
    })

    # Check the response
    assert resp.status_code == 200
    assert resp.json is not None
    assert 'success' in resp.json
    assert resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'Created filter.'

    # Check that the filter was created
    assert 'newfilter' in mock_filters


def test_post_duplicate(client):
    fake_login(client)

    # Test that the server won't error on duplicate filters but won't create duplicates
    client.post(url_for('api_v1.filters.create_filter'), json={
        'filter': 'newfilter'
    })
    assert 'newfilter' in mock_filters

    resp = client.post(url_for('api_v1.filters.create_filter'), json={
        'filter': 'newfilter'
    })

    # Check the response
    assert resp.status_code == 200
    assert resp.json is not None
    assert 'success' in resp.json
    assert resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'Created filter.'

    # Check that the filter wasn't duplicated
    assert mock_filters.count('newfilter') == 1


def test_delete_no_auth(client):
    # Test that an unauthenticated user can't delete filters
    resp = client.delete(url_for('api_v1.filters.delete_filter'), json={
        'filter': 'testing'
    })

    # Check the response
    assert resp.status_code == 401
    assert resp.json is None

    # Check that no changes were made
    assert 'testing' in mock_filters


def test_delete_missing(client):
    fake_login(client)

    # Test that a filter won't be deleted if one isn't specified
    resp = client.delete(url_for('api_v1.filters.delete_filter'), json={})
    
    # Check the response
    assert resp.status_code == 400
    assert resp.json is not None
    assert 'success' in resp.json
    assert not resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'Missing or invalid filter.'

    # Check that no changes were made
    assert mock_filters == ['abc', '123', 'testing']


def test_delete_invalid(client):
    fake_login(client)

    # Test that a filter won't be deleted if an invalid one is specified
    resp = client.delete(url_for('api_v1.filters.delete_filter'), json={
        'filter': 1
    })

    # Check the response
    assert resp.status_code == 400
    assert resp.json is not None
    assert 'success' in resp.json
    assert not resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'Missing or invalid filter.'

    # Check that no changes were made
    assert mock_filters == ['abc', '123', 'testing']


def test_delete_404(client):
    fake_login(client)

    # Test that a filter won't be deleted if it doesn't exist
    resp = client.delete(url_for('api_v1.filters.delete_filter'), json={
        'filter': 'fakefilter'
    })

    # Check the response
    assert resp.status_code == 404
    assert resp.json is not None
    assert 'success' in resp.json
    assert not resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'Filter does not exist.'

    # Check that no changes were made
    assert mock_filters == ['abc', '123', 'testing']


def test_delete_auth(client):
    fake_login(client)

    # Test that a filter will be deleted when authenticated
    resp = client.delete(url_for('api_v1.filters.delete_filter'), json={
        'filter': 'testing'
    })

    # Check the response
    assert resp.status_code == 200
    assert resp.json is not None
    assert 'success' in resp.json
    assert resp.json['success']
    assert 'message' in resp.json
    assert resp.json['message'] == 'Deleted filter.'

    # Check that the filter was deleted
    assert mock_filters == ['abc', '123']
