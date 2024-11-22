import canvasapi.exceptions
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file, after_this_request
from flask_login import current_user
import os

import utils.canvas as canvas_api
import utils.files as files
import utils.queries as queries
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
def get_all_courses(canvas_key: str | None = None) -> list:  # noqa: C901
    """
    Returns a list of all courses associated with the Canvas API key.

    :param canvas_key: If called directly, the function will use this API key to make any API calls.
    :return list: If manually called, this function will return a list of all courses. Otherwise, it
    will return a tuple of the form (Flask Response, status code).
    """

    if canvas_key is None:
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

    except AttributeError:
        if raw_data:
            return []
        return 'Unable to get field for courses', 404
    except Exception:
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

    except AttributeError:
        return 'Unable to get field for courses', 404
    except Exception:
        return 'Unable to make request to Canvas API', 400
    return jsonify(course_info), 200


@courses.get('/<courseid>/submissions')
def get_course_submissions(courseid):
    canvas_key = decrypt_canvas_key()

    try:
        # Construct a file prefix name
        course = canvas_api.get_course(canvas_key, courseid)
        if course is None:
            raise canvasapi.exceptions.Forbidden('Course not found')

        course_name = course.name
        today = datetime.now().strftime('%Y-%m-%d')
        file_name = f'{course_name}_submissions_{today}'

        # Get all submissions in a course
        submissions = canvas_api.get_course_submissions(canvas_key, courseid)

        # Download them to disk
        download_dir = canvas_api.download_submissions(submissions)

        # Zip the files
        zip_file = files.zip_folder(download_dir, dirname=file_name, delete_dir=True)

        # Handle cleaning up the archive after the request
        @after_this_request
        def delete_archive(response):
            # Delete the archive
            try:
                os.remove(zip_file)
            except Exception as e:
                print(e)

            return response

        # Send the file
        return send_file(zip_file, download_name=f'{file_name}.zip')

    except canvasapi.exceptions.Forbidden:
        # Convert 403 to 404 since we don't know if the ID is bad or non-existent. From the user's
        # perspective, it's like it doesn't exist.
        return jsonify({'success': False, 'message': 'Course not found.'}), 404

    except TypeError:
        # Thrown if courseid can't be interpreted as an int
        return jsonify({'success': False, 'message': 'Course ID must be an integer.'}), 400

    except Exception:
        return jsonify({'success': False, 'message': 'An unknown error occurred.'}), 500


@courses.get('/<courseid>/undated_assignments')
def get_undated_assignments(courseid):
    try:
        canvas_key = decrypt_canvas_key()

        assignments = canvas_api.get_undated_assignments(canvas_key, courseid)

        # Filter for relevant fields
        assignments = [canvas_api.assignment_to_dict(assignment) for assignment in assignments]

        # Check if any of them have user-defined due dates
        due_date_lookup = queries.get_custom_due_dates_by_ids(
            current_user,
            [assignment['id'] for assignment in assignments if assignment['id'] is not None]
        )
        for assignment in assignments:
            due_date = due_date_lookup.get(assignment['id'], None)
            assignment['due_at'] = due_date

        for assignment in assignments:
            # Translate 'name' to 'title' for the API
            assignment['title'] = assignment['name']
            del assignment['name']

            # Set it to be an assignment
            assignment['type'] = 'assignment'

            # Override the description to be None to save on bandwidth
            assignment['description'] = None

        return jsonify(assignments), 200
    except Exception:
        return jsonify({'success': False, 'message': 'An unknown error has occurred'}), 500


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
        print(e)
        return 'Unable to make request to Canvas API', 400
    except AttributeError:
        return 'Unable to get field for graded assignments', 404
    return jsonify(graded_assignments), 200


# Get all assignments for a course
@courses.route('/<courseid>/assignments', methods=['GET'])
def get_course_assignments(courseid, canvas_key: str | None = None):
    """
    Returns a list of all assignments for a course.

    :param canvas_key: If called directly, the function will use this API key to make any API calls.
    :return list: If manulaly called, this function will return a list of all assignments for the
    course. Otherwise, it will return a tuple of the form (Flask Response, status code).
    """

    if canvas_key is None:
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

    except AttributeError:
        if raw_data:
            print(f'Attribute error while getting assignments for {courseid}..')
            return []
        return 'Unable to get field for courses', 404
    except Exception:
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

    except Exception:
        return 'Unable to make request to Canvas API', 400
    except AttributeError:
        return 'Unable to get field for courses', 404
    return jsonify(assignment_dict), 200


@courses.post('/<courseid>/assignments/<assignmentid>/custom_due_date')
def set_custom_due_date(courseid, assignmentid):
    due_date = request.json.get('due_date', None)
    if due_date is None or type(due_date) is not str:
        return jsonify({'success': False, 'message': 'Missing or invalid due_date.'}), 400
    if len(due_date) > 20:
        return jsonify({'success': False, 'message': 'due_date is 20 characters at most.'}), 400

    try:
        canvas_key = decrypt_canvas_key()

        assignment = canvas_api.get_course_assignment(canvas_key, courseid, assignmentid)
        queries.set_custom_due_date_by_id(current_user, assignment.id, due_date)
    except ValueError:
        return jsonify({'success': False, 'message': 'ID does not exist.'}), 404
    except Exception:
        return jsonify({'success': False, 'message': 'An unknown error has occurred.'}), 500

    return jsonify({'success': True, 'message': 'Update custom due date.'})


@courses.route('/get_emails/<courseid>', methods=['GET'])
def get_professor_ta_ids(courseid):
    canvas_key = decrypt_canvas_key()

    try:
        professor_ta_ids = canvas_api.get_professor_info(canvas_key, courseid)

    except Exception:
        return 'Unable to make request to Canvas API', 400
    except AttributeError:
        return 'Unable to get field for users in course', 404
    return jsonify(professor_ta_ids), 200


@courses.route('/get_grade_simulation/<courseid>', methods=['GET'])
def get_grade_simulation(courseid):
    canvas_key = decrypt_canvas_key()

    try:
        grade_weight_group = canvas_api.get_weighted_graded_assignments_for_course(canvas_key,
                                                                                   courseid)
        if grade_weight_group is None:
            return "Invalid course id", 400

        grade_log = []
        for section in grade_weight_group:
            grade_section = {
                'name': getattr(section, 'name', None),
                'weight': getattr(section, 'group_weight', None),
                'assignments': [
                    {
                        'name': assignment.get('name', None),
                        'max_score': assignment.get('points_possible', None),
                        'score': assignment.get('submission', {}).get('score', None)
                        if assignment.get('submission') else None,
                        'omit_from_final_grade': assignment.get('omit_from_final_grade', None)
                    }
                    for assignment in getattr(section, 'assignments', [])
                ]
            }
            grade_log.append(grade_section)

    except Exception:
        return 'Unable to make request to Canvas API', 400
    except AttributeError:
        return 'Unable to get field for assignment', 404
    return jsonify(grade_log), 200
