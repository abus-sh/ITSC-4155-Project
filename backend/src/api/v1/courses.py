from canvasapi import Canvas
from datetime import datetime
from flask import Blueprint, jsonify

from utils.session import decrypt_canvas_key
from utils.settings import get_canvas_url


courses = Blueprint('courses', __name__)
BASE_URL = get_canvas_url()


def get_term() -> tuple[str, str]:
    """Returns current year and semester."""
    current_year = str(datetime.now().year)
    now = datetime.now()
    month = now.month
    day = now.day
    # Summer classes start in middle of May, and Fall classes start in middle of August, 
    # so we need the day to be precise
    if (1 <= month <= 4) or (month == 5 and day <= 15):
        current_semester = '10'  # Spring
    elif (month == 5 and day > 20) or (month == 6) or (month == 7) or (month == 8 and day <= 10):
        current_semester = '60'  # Summer
    else:
        current_semester = '80'  # Fall
    return (current_semester, current_year)


# ENDPOINT: /api/v1/courses/

# Get list of all courses for current student
@courses.route('/all', methods=['GET'])
def get_all_courses():
    canvas_key = decrypt_canvas_key()
    current_semester, current_year = get_term()

    try:
        canvas = Canvas(BASE_URL, canvas_key)
        current_courses = canvas.get_courses(enrollment_state='active', include=["total_scores", "term", "concluded"])
        courses_list = []
        fields = [
            'id', 'name', 'uuid', 'course_code', 'calendar', 'enrollments', 'term', 'concluded'
            ]
        for course in current_courses:
            # Some courses, like the `Training Supplement`, are never considered to be concluded,
            # so we still need to filter by semester, but using concluded will make it much faster
            # to skip all other courses
            if getattr(course, 'concluded', True):
                continue
            name = getattr(course, 'name', None)
            if name:
                term = name.split('-')[0]
                semester, year = term[-2:], term[:-2]
                if year != current_year or semester != current_semester:
                    continue
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
        course = Canvas(BASE_URL, canvas_key).get_course(courseid)
        course_assignments = course.get_assignments()
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