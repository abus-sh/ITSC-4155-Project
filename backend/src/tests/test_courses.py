import canvasapi.exceptions
from flask import url_for
import pytest

import api.v1.courses as courses
import utils.queries as queries
import utils.canvas as utils_canvas

#################################################################
#                                                               #
#                           MOCK DATA                           #
#                                                               #
#################################################################


class MockCanvas:
    def __init__(self, base_url: str, access_token: str):
        self.base_url = base_url
        self.access_token = access_token

    def get_current_user(self):
        return MockCanvasUser(-1, 'canvas_test')

    def get_courses(self, enrollment_state: str, include: list[str] = []):
        return mock_courses

    def get_course(self, course_id, include: list[str] = []):
        if not course_id.isnumeric():
            raise TypeError

        for course in mock_courses:
            if course.id == course_id:
                return course

        return None


class MockCanvasUser:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class MockCourse:
    def __init__(self, id: int, name: str, uuid: str, term: str, concluded: bool):
        self.id = id
        self.name = name
        self.uuid = uuid
        self.term = term
        self.concluded = concluded
        self.assignments = [
            MockAssignment('1', '1', self.id, 100, 'now', attachments=[
                MockAttachment()
            ]),
            MockAssignment('2', '2', self.id, 90, 'past'),
            MockAssignment('3', '3', self.id, 80, 'future'),
        ]

    def get_multiple_submissions(self, workflow_state='graded', include=['assignment']):
        return self.assignments

    def get_assignments(self):
        return self.assignments

    def get_assignment(self, assignment_id):
        for assignment in self.assignments:
            if assignment.id == assignment_id:
                return assignment

        return None


class MockAssignment:
    def __init__(self, id, assignment_id, course_id, score, due_at, attachments = []):
        self.id = id
        self.assignment_id = assignment_id
        self.course_id = course_id
        self.score = score
        self.due_at = due_at
        self.attachments = attachments


class MockAttachment:
    def download(self, path: str):
        # Intentional no-op
        pass


mock_courses = [
    MockCourse('1', '202480-ITSC-4155-001-12770', '1', 'faketerm', False),
    MockCourse('2', '202480-FAKE-1337-002-12771', '2', 'faketerm', False),
    MockCourse('3', '202380-FAKE-1000-003-12772', '3', 'faketerm', True)
]


class MockTodoistAPI:
    def __init__(self, todoist_token):
        self.todoist_token = todoist_token

    def get_task(self, task_id):
        pass


def mock_decrypt_canvas_key():
    return 'ctoken'


@pytest.fixture(autouse=True)
def init_test(monkeypatch):
    monkeypatch.setattr(queries, 'Canvas', MockCanvas)
    monkeypatch.setattr(utils_canvas, 'Canvas', MockCanvas)
    monkeypatch.setattr(queries, 'TodoistAPI', MockTodoistAPI)
    monkeypatch.setattr(courses, 'decrypt_canvas_key', mock_decrypt_canvas_key)


def fake_login(client):
    test_user = {
        'username': 'test',
        'password': 'testtesttesttest',
        'canvasToken': 'ctoken',
        'todoistToken': 'ttoken'
    }

    resp = client.post(url_for('authentication.sign_up'), json=test_user)
    assert resp.status_code == 200 or resp.status_code == 500

    resp = client.post(url_for('authentication.login'), json=test_user)
    assert resp.status_code == 200


#################################################################
#                                                               #
#                           UNIT TESTS                          #
#                                                               #
#################################################################


def test_get_all_courses(client):
    # Check that an unauthenticated user can't access courses
    resp = client.get(url_for('api_v1.courses.get_all_courses'))
    assert resp.status_code == 401
    assert resp.json is None

    # Check that an authenticated user can access courses

    fake_login(client)
    resp = client.get(url_for('api_v1.courses.get_all_courses'))
    assert resp.status_code == 200
    assert type(resp.json) is list

    course = resp.json[0]
    assert 'id' in course
    assert course['id'] == '1'
    assert 'name' in course
    assert course['name'] == '202480-ITSC-4155-001-12770'
    assert 'term' in course
    assert course['term'] == 'faketerm'


def test_get_course(client):
    # Check that an unauthenticated user can't access a course
    resp = client.get(url_for('api_v1.courses.get_course', courseid=1))
    assert resp.status_code == 401
    assert resp.json is None

    fake_login(client)

    # Check that course ID 1 exists
    resp = client.get(url_for('api_v1.courses.get_course', courseid=1))
    assert resp.status_code == 200
    assert type(resp.json) is dict

    course = resp.json
    assert 'id' in course
    assert course['id'] == '1'
    assert 'name' in course
    assert course['name'] == '202480-ITSC-4155-001-12770'
    assert 'term' in course
    assert course['term'] == 'faketerm'

    # Check that course ID 2 exists
    resp = client.get(url_for('api_v1.courses.get_course', courseid=2))
    assert resp.status_code == 200
    assert type(resp.json) is dict

    course = resp.json
    assert 'id' in course
    assert course['id'] == '2'
    assert 'name' in course
    assert course['name'] == '202480-FAKE-1337-002-12771'
    assert 'term' in course
    assert course['term'] == 'faketerm'

    # Check a fake ID
    resp = client.get(url_for('api_v1.courses.get_course', courseid=100))

    course = resp.json
    assert 'id' in course
    assert course['id'] is None
    assert 'name' in course
    assert course['name'] is None
    assert 'term' in course
    assert course['term'] is None


def test_graded_assignments(client):
    # Check that an unauthenticated user can't access graded assignments
    resp = client.post(url_for('api_v1.courses.get_graded_assignments'), json={'course_id': '1'})
    assert resp.status_code == 401
    assert resp.json is None

    fake_login(client)

    # Check that an authenticates user can accses graded assignments
    resp = client.post(url_for('api_v1.courses.get_graded_assignments'), json={'course_id': '1'})
    assert resp.status_code == 200
    assert type(resp.json) is list

    assignments = resp.json
    assert assignments[0]['id'] == '1'
    assert assignments[0]['score'] == 100
    assert assignments[1]['id'] == '2'
    assert assignments[1]['score'] == 90
    assert assignments[2]['id'] == '3'
    assert assignments[2]['score'] == 80


def test_get_course_assignments(client):
    # Check that an unauthenticated user can't access assignments
    resp = client.get(url_for('api_v1.courses.get_course_assignments', courseid=1))
    assert resp.status_code == 401
    assert resp.json is None

    fake_login(client)

    # Check that an authenticated user can access assignments
    resp = client.get(url_for('api_v1.courses.get_course_assignments', courseid=1))
    assert resp.status_code == 200
    assert type(resp.json) is list

    assignments = resp.json
    assert assignments[0]['id'] == '1'
    assert assignments[0]['due_at'] == 'now'
    assert assignments[1]['id'] == '2'
    assert assignments[1]['due_at'] == 'past'
    assert assignments[2]['id'] == '3'
    assert assignments[2]['due_at'] == 'future'


def test_get_course_assignment(client):
    # Check that an unauthenticated user can't access assignments
    resp = client.get(url_for('api_v1.courses.get_course_assignment', courseid=1, assignmentid=1))
    assert resp.status_code == 401
    assert resp.json is None

    fake_login(client)

    # Check that an authenticated user can access assignments
    resp = client.get(url_for('api_v1.courses.get_course_assignment', courseid=1, assignmentid=1))
    assert resp.status_code == 200
    assert type(resp.json) is dict

    assignment = resp.json
    assert assignment['course_id'] == '1'
    assert assignment['id'] == '1'

    resp = client.get(url_for('api_v1.courses.get_course_assignment', courseid=1, assignmentid=2))
    assert resp.status_code == 200
    assert type(resp.json) is dict

    assignment = resp.json
    assert assignment['course_id'] == '1'
    assert assignment['id'] == '2'

    resp = client.get(url_for('api_v1.courses.get_course_assignment', courseid=1, assignmentid=100))
    assert resp.status_code == 200
    assert type(resp.json) is dict

    assignment = resp.json
    assert assignment['course_id'] is None
    assert assignment['id'] is None


def test_get_course_submissions(client, monkeypatch):
    # Check that an unauthenticated user can't download submissions
    resp = client.get(url_for('api_v1.courses.get_course_submissions', courseid=1))
    assert resp.status_code == 401
    assert resp.json is None

    fake_login(client)

    # Check a non-existent course
    resp = client.get(url_for('api_v1.courses.get_course_submissions', courseid=100))
    assert resp.status_code == 404
    assert resp.json is not None
    assert not resp.json['success']
    assert resp.json['message'] == 'Course not found.'

    # Check a bad course
    resp = client.get(url_for('api_v1.courses.get_course_submissions', courseid='a'))
    assert resp.status_code == 400
    assert resp.json is not None
    assert not resp.json['success']
    assert resp.json['message'] == 'Course ID must be an integer.'

    # Check that a ZIP is returned for a valid course
    resp = client.get(url_for('api_v1.courses.get_course_submissions', courseid=1))
    assert resp.status_code == 200
    assert resp.json is None
    assert resp.text.startswith('PK')  # Check magic bytes for ZIP file
