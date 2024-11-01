from canvasapi.assignment import Assignment
from canvasapi.course import Course
from datetime import datetime
from flask import Blueprint, jsonify, request

import utils.canvas as canvas_api
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
        current_courses = canvas_api.get_all_courses(canvas_key)

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
            one_course = canvas_api.course_to_dict(course)
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
        course = canvas_api.get_course(canvas_key, courseid)
        course_info = canvas_api.course_to_dict(course)

    except AttributeError as e:
        return 'Unable to get field for courses', 404
    except Exception as e:
        return 'Unable to make request to Canvas API', 400
    return jsonify(course_info), 200


@courses.route('/graded_assignments', methods=['GET', 'POST'])
def get_graded_assignments():
    try:
        # Get course id in body json
        course_id = request.json.get('course_id')
        if not course_id:
            return jsonify("Invalid course_id!"), 400

        canvas_key = decrypt_canvas_key()
        assignments = canvas_api.get_graded_assignments(canvas_key, course_id)

        graded_assignments = []
        for graded in assignments:
            fields = [
                'id', 'grade', 'score', 'assignment_id', 'late', 'course_id', 'late',
                'points_deducted', 'excused', 'attempt', 'graded_at', 'submitted_at', 'body',
            ]
            extra_fields = [
                'html_url', 'name', 'points_possible'
            ]
            one_graded = {field: getattr(graded, field, None) for field in fields}
            # Fields inside the assignment dict
            assignment_details = getattr(graded, 'assignment', None)
            if assignment_details:
                for extra_field in extra_fields:
                    one_graded[extra_field] = assignment_details.get(extra_field, None)

            graded_assignments.append(one_graded)
    except Exception as e:
        return 'Unable to make request to Canvas API', 400
    except AttributeError as e:
        return 'Unable to get field for graded assignments', 404
    return jsonify(graded_assignments), 200


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
        course_assignments = canvas_api.get_course_assignments(canvas_key, courseid)
        assignments = []
        for assignment in course_assignments:
            assignment_dict = canvas_api.assignment_to_dict(assignment)
            assignments.append(assignment_dict)

    except AttributeError as e:
        if raw_data:
            print(f'Attribute error while getting assignments for {courseid}..')
            return []
        return 'Unable to get field for courses', 404
    except Exception as e:
        if raw_data:
            print(f'Exception while getting assignments for {courseid}..')
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
        assignment = canvas_api.get_course_assignment(canvas_key, courseid, assignmentid)
        assignment_dict = canvas_api.assignment_to_dict(assignment)

    except Exception as e:
        return 'Unable to make request to Canvas API', 400
    except AttributeError as e:
        return 'Unable to get field for courses', 404
    return jsonify(assignment_dict), 200

# TO DO:
# GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions (List assignment submissions)
# GET /api/v1/courses/:course_id/students/submissions (List submissions for multiple assignments)
# GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id (Get a single submission)
