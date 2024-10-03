from canvasapi import Canvas
from flask import Blueprint, jsonify

from utils.session import decrypt_canvas_key
from utils.settings import get_canvas_url


courses = Blueprint('courses', __name__)
BASE_URL = get_canvas_url()


# Get list of all courses for current student
@courses.route('/all', methods=['GET'])
def get_all_courses():
    canvas_key = decrypt_canvas_key()

    try:
        canvas = Canvas(BASE_URL, canvas_key)
        current_courses = canvas.get_courses(enrollment_state='active', include=["total_scores"])
        courses_list = []
        fields = [
            'id', 'name', 'uuid', 'course_code', 'calendar', 'enrollments'
            ]
        for course in current_courses:
            one_course = {field: getattr(course, field, None) for field in fields}
            courses_list.append(one_course)
            
    except Exception as e:
        return 'Unable to make request to Canvas API', 400
    except AttributeError as e:
        return 'Unable to get field for courses', 404
    return jsonify(courses_list), 200


# Get info about a single course
@courses.route('/<courseid>', methods=['GET'])
def get_course(courseid):
    canvas_key = decrypt_canvas_key()

    try:
        canvas = Canvas(BASE_URL, canvas_key)
        course = canvas.get_course(courseid, include=["total_scores"])
        fields = [
            'id', 'name', 'uuid', 'course_code', 'calendar', 'enrollments'
            ]
        course_info = {field: getattr(course, field, None) for field in fields}
            
    except Exception as e:
        return 'Unable to make request to Canvas API', 400
    except AttributeError as e:
        return 'Unable to get field for courses', 404
    return jsonify(course_info), 200


# Get all assignments for a course
@courses.route('/<courseid>/assignments', methods=['GET'])
def get_course_assignments(courseid):
    canvas_key = decrypt_canvas_key()

    try:
        current_user = Canvas(BASE_URL, canvas_key).get_current_user()
        course_assignments = current_user.get_assignments(courseid)
        assignments = []
        fields = [
            'id', 'name', 'due_at', 'points_possible', 'omit_from_final_grade', 
            'allowed_attempts', 'course_id', 'submission_types', 'has_submitted_submissions', 
            'is_quiz_assignment', 'html_url', 'quiz_id', 'submissions_download_url', 
            'require_lockdown_browser'
        ]
        for assignment in course_assignments:
            assignment_dict = {field: getattr(assignment, field, None) for field in fields}
            assignments.append(assignment_dict)

    except Exception as e:
        return 'Unable to make request to Canvas API', 400
    except AttributeError as e:
        return 'Unable to get field for courses', 404
    return jsonify(assignments), 200


# Get a single assignment for a course
@courses.route('/<courseid>/assignments/<assignmentid>', methods=['GET'])
def get_course_assignment(courseid, assignmentid):
    canvas_key = decrypt_canvas_key()

    try:
        canvas = Canvas(BASE_URL, canvas_key)
        assignment = canvas.get_course(courseid).get_assignment(assignmentid)
        fields = [
            'id', 'name', 'description', 'due_at', 'lock_at', 'course_id', 'html_url', 
            'submissions_download_url', 'allowed_extensions', 'turnitin_enabled', 
            'grade_group_students_individually', 'group_category_id', 'points_possible', 
            'submission_types', 'published', 'quiz_id', 'omit_from_final_grade', 
            'allowed_attempts', 'can_submit', 'is_quiz_assignment', 'workflow_state'
        ]
        assignment_dict = {field: getattr(assignment, field, None) for field in fields}

    except Exception as e:
        return 'Unable to make request to Canvas API', 400
    except AttributeError as e:
        return 'Unable to get field for courses', 404
    return jsonify(assignment_dict), 200

# TO DO:
# GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions (List assignment submissions)
# GET /api/v1/courses/:course_id/students/submissions (List submissions for multiple assignments)
# GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id (Get a single submission)
