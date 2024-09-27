from flask import Blueprint, jsonify
from canvasapi import Canvas
from utils.core import get_token_for_testing

api_v1 = Blueprint('ap1_v1', __name__)

TOKEN = get_token_for_testing()
BASE_URL = "https://uncc.instructure.com"

@api_v1.route('/courses/all', methods=['GET'])
def get_all_tasks():
    try:
        canvas = Canvas(BASE_URL, TOKEN)
        current_courses = canvas.get_courses(enrollment_state='active')
        courses = []
        for course in current_courses:
            course_dict = {
                'id': getattr(course, 'id', None),
                'name': getattr(course, 'name', None),
                'uuid': getattr(course, 'uuid', None),
                'course_code': getattr(course, 'course_code', None),
                'calendar': getattr(course, 'calendar', None),
            }
            courses.append(course_dict)
    except Exception as e:
        return 'Unable to make request to Canvas API', 400
    except AttributeError as e:
        return 'Unable to get field for courses', 404
    return jsonify(courses), 200


@api_v1.route('/courses/<courseid>/assignments', methods=['GET'])
def get_course_assignments(courseid):
    try:
        current_user = Canvas(BASE_URL, TOKEN).get_current_user()
        course_assignments = current_user.get_assignments(courseid)
        assignments = []
        for assignment in course_assignments:
            assignment_dict = {
                'id': getattr(assignment, 'id', None),
                'name': getattr(assignment, 'name', None),
                'due_at': getattr(assignment, 'due_at', None),
                'points_possible': getattr(assignment, 'points_possible', None),
                'omit_from_final_grade': getattr(assignment, 'omit_from_final_grade', None),
                'allowed_attempts': getattr(assignment, 'allowed_attempts', None),
                'course_id': getattr(assignment, 'course_id', None),
                'submission_types': getattr(assignment, 'submission_types', None),
                'has_submitted_submissions': getattr(assignment, 'has_submitted_submissions', None),
                'is_quiz': getattr(assignment, 'is_quiz_assignment', None),
                'canvas_url': getattr(assignment, 'html_url', None),
                'quiz_id': getattr(assignment, 'quiz_id', None),
                'submissions_download_url': getattr(assignment, 'submissions_download_url', None),
                'require_lockdown_browser': getattr(assignment, 'require_lockdown_browser', None),
            }
            assignments.append(assignment_dict)
    except Exception as e:
        print(e)
        return 'Unable to make request to Canvas API', 400
    except AttributeError as e:
        return 'Unable to get field for courses', 404
    return jsonify(assignments), 200


@api_v1.route('/courses/<courseid>/assignments/<assignmentid>', methods=['GET'])
def get_assignment(courseid, assignmentid):
    try:
        canvas = Canvas(BASE_URL, TOKEN)
        course = canvas.get_course(courseid)
        assignment = course.get_assignment(assignmentid)
        # TO DO
    except Exception as e:
        return 'Unable to make request to Canvas API', 400
    except AttributeError as e:
        return 'Unable to get field for courses', 404
    return '', 200