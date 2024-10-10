from canvasapi import Canvas
from canvasapi.assignment import Assignment
from canvasapi.course import Course
from datetime import datetime
from flask import Blueprint, jsonify

from utils.session import decrypt_canvas_key
from utils.settings import get_canvas_url


courses = Blueprint('courses', __name__)
BASE_URL = get_canvas_url()

# Custom parameters to get from the Canvas API for course requests
# Specified here to ensure standardization.
CUSTOM_COURSE_PARAMS = [
    "total_scores", "term", "concluded", "course_image"
]

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
def get_all_courses(canvas_key: str|None=None) -> list:
    """
    Returns a list of all courses associated with the Canvas API key.

    :param canvas_key: If called directly, the function will use this API key to make any API calls.
    :return list: If manually called, this function will return a list of all courses. Otherwise, it
    will return a tuple of the form (Flask Response, status code).
    """

    if canvas_key == None:
        canvas_key = decrypt_canvas_key()
        raw_data = False
    else:
        raw_data = True
    current_semester, current_year = get_term()

    try:
        canvas = Canvas(BASE_URL, canvas_key)
        current_courses = canvas.get_courses(enrollment_state='active',
                                             include=CUSTOM_COURSE_PARAMS)
        courses_list = []
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
            one_course = _course_to_dict(course)
            courses_list.append(one_course)

    except AttributeError as e:
        if raw_data:
            return []
        return 'Unable to get field for courses', 404
    except Exception as e:
        if raw_data:
            return []
        return 'Unable to make request to Canvas API', 400
    
    if raw_data:
        return courses_list
    return jsonify(courses_list), 200


# Get info about a single course
@courses.route('/<courseid>', methods=['GET'])
def get_course(courseid):
    canvas_key = decrypt_canvas_key()

    try:
        canvas = Canvas(BASE_URL, canvas_key)
        course = canvas.get_course(courseid, include=CUSTOM_COURSE_PARAMS)
        course_info = _course_to_dict(course)
            
    except Exception as e:
        return 'Unable to make request to Canvas API', 400
    except AttributeError as e:
        return 'Unable to get field for courses', 404
    return jsonify(course_info), 200


# Get all assignments for a course
@courses.route('/<courseid>/assignments', methods=['GET'])
def get_course_assignments(courseid, canvas_key: str|None=None):
    """
    Returns a list of all assignments for a course.

    :param canvas_key: If called directly, the function will use this API key to make any API calls.
    :return list: If manulaly called, this function will return a list of all assignments for the
    course. Otherwise, it will return a tuple of the form (Flask Response, status code).
    """

    if canvas_key == None:
        canvas_key = decrypt_canvas_key()
        raw_data = False
    else:
        raw_data = True

    try:
        course = Canvas(BASE_URL, canvas_key).get_course(courseid)
        course_assignments = course.get_assignments()
        assignments = []
        for assignment in course_assignments:
            assignment_dict = _assignment_to_dict(assignment)
            assignments.append(assignment_dict)

    except AttributeError as e:
            if raw_data:
                return []
            return 'Unable to get field for courses', 404
    except Exception as e:
        if raw_data:
            return []
        return 'Unable to make request to Canvas API', 400
    if raw_data:
        return assignments
    return jsonify(assignments), 200


# Get a single assignment for a course
@courses.route('/<courseid>/assignments/<assignmentid>', methods=['GET'])
def get_course_assignment(courseid, assignmentid):
    canvas_key = decrypt_canvas_key()

    try:
        canvas = Canvas(BASE_URL, canvas_key)
        assignment = canvas.get_course(courseid).get_assignment(assignmentid)
        assignment_dict = _assignment_to_dict(assignment)

    except Exception as e:
        return 'Unable to make request to Canvas API', 400
    except AttributeError as e:
        return 'Unable to get field for courses', 404
    return jsonify(assignment_dict), 200

# TO DO:
# GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions (List assignment submissions)
# GET /api/v1/courses/:course_id/students/submissions (List submissions for multiple assignments)
# GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id (Get a single submission)

def _course_to_dict(course: Course, fields: list[str]|None=None) -> dict[str, str|None]:
    """
    Converts a course into a dict, taking only the fields specified in fields. If fields is None,
    then a default set of fields are used.

    :param course: The course to convert to a dict.
    :param fields: The fields to extract from the course. If fields is not specified, a default list
    of fields are used instead.
    :return dict[str, str|None]: Returns a dict with each key. If no value was present for the key,
    None is returned instead.
    """
    if fields == None:
        fields = [
            'id', 'name', 'uuid', 'course_code', 'calendar', 'enrollments', 'term', 'concluded',
            'image_download_url'
        ]

    return {field: getattr(course, field, None) for field in fields}

def _assignment_to_dict(assignment: Assignment, fields: list[str]|None=None) -> dict[str, str|None]:
    """
    Converts an assignment into a dict, taking only the fields specified in fields. If fields is
    None, then a default set of fields are used.

    :param assignment: The assignment to convert to a dict.
    :param fields: The fields to extract from the assignment. If fields is not specified, a default
    list of fields are used instead.
    :return dict[str, str|None]: Returns a dict with each key. If no value was present for the key,
    None is returned instead.
    """
    if fields == None:
        fields = [
            'id', 'name', 'description', 'due_at', 'lock_at', 'course_id', 'html_url', 
            'submissions_download_url', 'allowed_extensions', 'turnitin_enabled', 
            'grade_group_students_individually', 'group_category_id', 'points_possible', 
            'submission_types', 'published', 'quiz_id', 'omit_from_final_grade', 
            'allowed_attempts', 'can_submit', 'is_quiz_assignment', 'workflow_state'
        ]

    return {field: getattr(assignment, field, None) for field in fields}
