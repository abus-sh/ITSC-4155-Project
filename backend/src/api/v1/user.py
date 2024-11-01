from flask import Blueprint, jsonify, request
from flask_login import current_user
from datetime import datetime


import utils.canvas as canvas_api
from utils.session import decrypt_canvas_key
from utils.settings import get_canvas_url, get_date_range, localize_date, date_passed

import utils.queries as queries
import utils.models as models

user = Blueprint('user', __name__)
BASE_URL = get_canvas_url()

# ENDPOINT: /api/v1/user/


@user.route('/profile', methods=['GET'])
def get_user_info():
    try:
        canvas_key = decrypt_canvas_key()
        profile = canvas_api.get_current_user(canvas_key)
        user_profile = {
            'username': current_user.username,
            'canvas': {
                'canvas_id': current_user.canvas_id,
                'canvas_name': current_user.canvas_name,
                'canvas_title': getattr(profile, 'title', None),
                'canvas_bio': getattr(profile, 'bio', None),
                'canvas_pic': getattr(profile, 'avatar_url', None)
                }
            }

    except Exception:
        return 'Unable to make request to Canvas API', 400
    except AttributeError:
        return 'Unable to get field for request', 404
    return jsonify(user_profile), 200


# Get Assignments due this month
@user.route('/due_soon', methods=['GET'])
def get_assignments_due_soon():
    try:
        canvas_key = decrypt_canvas_key()

        # Get assignments that have due date between today and 1 month from now
        start_date, end_date = get_date_range(months=1)

        assignments_due_soon = []

        # Get non-Canvas tasks
        tasks: list[models.Task] = queries.get_non_canvas_tasks(current_user)
        for task in tasks:
            data = {
                'title': task.name,
                'description': task.description,
                'type': 'assignment',
                'submission_types': [],
                'graded_submissions_exist': False,
                'due_at': task.due_date,
                'subtasks': []
            }
            assignments_due_soon.append(data)

        assignments = canvas_api.get_calendar_events(canvas_key, start_date, end_date)

        fields = [
            'title', 'description', 'type', 'submission_types', 'html_url', 'context_name',
        ]
        extra_fields = [
            'id', 'points_possible', 'graded_submissions_exist', 'user_submitted'
        ]
        for assignment in assignments:

            # Basic fields
            one_assignment = {field: getattr(assignment, field, None) for field in fields}

            # Fields inside the assignment dict
            more_details = getattr(assignment, 'assignment', None)
            if more_details:
                for extra_field in extra_fields:
                    one_assignment[extra_field] = more_details.get(extra_field, None)

                # Get the due date; if it doesn't have one, use the lock at date
                due_date = more_details.get('due_at') or more_details.get('lock_at')

                # Skip assignment if no due date
                if not due_date:
                    continue

                parsed_due_date = localize_date(datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%SZ"))
                # Skip to the next iteration if the due date is older than yesterday
                if date_passed(parsed_due_date):
                    continue

                one_assignment['due_at'] = parsed_due_date.strftime('%Y-%m-%d %H:%M:%S')
            assignments_due_soon.append(one_assignment)

    except Exception as e:
        print(e)
        return 'Unable to make request to Canvas API', 400
    except AttributeError as e:
        print(e)
        return 'Unable to get field for courses', 404
    return jsonify(assignments_due_soon), 200


# Get missing submissions for active courses (past the due date)
@user.route('/missing_submissions', methods=['GET', 'POST'])
def get_missing_submissions():
    canvas_key = decrypt_canvas_key()

    try:
        # get courses ids from request json body
        if request.is_json:
            request_data = request.get_json()
            courses_list = request_data.get('course_ids', []) if request_data else []
        else:
            # If not JSON, use an empty list
            courses_list = []
        # If the course_ids were not provided, fetch them from the active enrollment canvas api
        if len(courses_list) <= 0:
            current_courses = canvas_api.get_all_courses()
            for course in current_courses:
                one_course = getattr(course, 'id', None)
                if one_course is not None:
                    courses_list.append(one_course)

        missing_submissions = canvas_api.get_missing_submissions(canvas_key,
                                                                 frozenset(courses_list))
        miss_assignments_list = []
        fields = [
            'id', 'name', 'description', 'due_at', 'course_id', 'html_url'
        ]
        for assignment in missing_submissions:
            miss_assignment = {field: getattr(assignment, field, None) for field in fields}
            miss_assignments_list.append(miss_assignment)
    except Exception as e:
        print(e)
        return 'Unable to make request to Canvas API', 400
    except AttributeError as e:
        print(e)
        return 'Unable to get field for courses', 404
    return jsonify(miss_assignments_list), 200


# Get calendar event for 1 month
@user.route('/calendar_events', methods=['GET'])
def get_calendar_events():
    try:
        canvas_key = decrypt_canvas_key()

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if start_date is None or end_date is None:
            return 'Invalid dates argument', 400

        # type event returns all the events, not just assignment
        all_events = canvas_api.get_all_calendar_events(canvas_key, start_date, end_date, limit=60,
                                                        event_types=['event', 'assignment'])

        fields = [
            'id', 'title', 'description', 'type', 'submission_types', 'html_url', 'context_name',
            'start_at', 'end_at'
        ]
        calendar_events = []
        for event in all_events:
            # Basic fields
            single_event = {field: getattr(event, field, None) for field in fields}

            if single_event['start_at'] is None:
                continue

            # If assignment was submitted
            assignment_details = getattr(event, 'assignment', None)
            if assignment_details:
                single_event['user_submitted'] = assignment_details.get('user_submitted', False)
            else:
                single_event['user_submitted'] = False

            calendar_events.append(single_event)

    except Exception as e:
        print(e)
        return 'Unable to make request to Canvas API', 400
    except AttributeError:
        return 'Unable to get field for calendar event', 404
    return jsonify(calendar_events), 200
