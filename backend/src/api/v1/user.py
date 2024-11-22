from flask import Blueprint, jsonify, request
from flask_login import current_user
from datetime import datetime
import utils.canvas as canvas_api
from utils.session import decrypt_canvas_key, decrypt_todoist_key
from utils.settings import get_canvas_url, get_date_range, localize_date, date_passed
from utils.todoist import add_shared_subtask
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
def get_assignments_due_soon():  # noqa: C901
    try:
        canvas_key = decrypt_canvas_key()

        # Get assignments that have due date between today and 1 month from now
        start_date, end_date = get_date_range(months=1)

        assignments_due_soon = []

        # Get non-Canvas tasks
        tasks: list[models.Task] = queries.get_non_canvas_tasks(current_user)
        for task in tasks:
            data = {
                'db_id': task.id,
                'title': task.name,
                'user_description': task.description,
                'type': 'assignment',
                'submission_types': [],
                'graded_submissions_exist': False,
                'due_at': task.due_date,
                'subtasks': []
            }
            assignments_due_soon.append(data)

        assignments = canvas_api.get_calendar_events(canvas_key, start_date, end_date)

        fields = [
            'title', 'type', 'submission_types', 'html_url', 'context_name', 'context_code'
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

        # Get all assignments that come from Canvas (i.e., have a Canvas ID)
        # Retrieve their descriptions from database
        canvas_assignments: dict[int, dict] = dict()
        for assignment in assignments_due_soon:
            if 'id' in assignment:
                canvas_assignments[assignment['id']] = assignment
        canvas_ids = [id for id in canvas_assignments]
        descriptions = queries.get_descriptions_by_canvas_ids(current_user, canvas_ids)

        # Update each Canvas assignment to include the database description
        for id in descriptions:
            canvas_assignments[id]['user_description'] = descriptions[id]

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


@user.route('/send_message', methods=['POST'])
def send_message_to_professor_ta():
    canvas_key = decrypt_canvas_key()

    try:
        data = request.json

        recipients = data.get('recipients')
        subject = data.get('subject').strip()
        body = data.get('body').strip()
        canvas_id = int(data.get('canvas_id'))

        if not recipients or not subject or not body or not isinstance(recipients, list) or not canvas_id:
            return 'Invalid payload', 400

        canvas_id, conv_exists = queries.valid_task_id(current_user, canvas_id)
        if not canvas_id:
            return 'Conversation associated with invalid task', 400

        conversation_id = canvas_api.send_message(canvas_key, recipients, subject, body, conv_exists)

        if not conversation_id:
            return 'Unable to send message', 400
        result = queries.create_new_conversation(current_user, canvas_id, conversation_id)
        if result is False:
            return 'Unable to create conversation successfully', 400

    except Exception as e:
        print(e)
        return 'Unable to make request to Canvas API', 400
    except AttributeError:
        return 'Unable to determine message fields', 404
    return jsonify('Message sent successfully!'), 200


@user.route('/reply_message', methods=['POST'])
def send_reply_conversation():
    canvas_key = decrypt_canvas_key()

    try:
        data = request.json
        conv_id = int(data.get('conversation_id'))
        reply_body = data.get('body').strip()

        conv_reply_id = canvas_api.send_reply(canvas_key, conv_id, reply_body)
        if conv_reply_id is None:
            return 'Unable to send reply to the Canvas api', 400

    except ValueError:
        return 'Invalid conversation id', 400
    except Exception:
        return 'Error while sending reply to the Canvas api', 400
    return jsonify('Reply sent successfully!'), 200


@user.route('/get_conversations/<canvas_id>', methods=['GET'])
def get_conversations(canvas_id):
    canvas_key = decrypt_canvas_key()

    try:
        canvas_id = int(canvas_id)
        if not canvas_id:
            return 'Invalid canvas id', 400

        conv_ids = queries.get_conversation_by_canvas_id(current_user, canvas_id)
        # No conversation was found from the database
        if len(conv_ids) < 1:
            return jsonify([]), 200
        # Get conversations from canvas using the ids
        conversations = canvas_api.get_conversations_from_ids(canvas_key, conv_ids)

    except ValueError:
        return 'Canvas id needs to be an integer', 400
    except Exception:
        return 'Unable to get conversations from the Canvas api', 400
    return jsonify(conversations), 200


@user.route('/get_notifications', methods=['GET'])
def get_notifications():
    try:
        invitations = queries.get_subtask_invitations(current_user)
        invitations_list = {'invitation': [], 'simple': []}

        if invitations:
            invitations_list['invitation'] = queries.compose_invitations(invitations)

    except Exception as e:
        print(e)
        return 'Unable to retrieve notifications', 400
    return jsonify(invitations_list), 200


@user.route('/send_invitation', methods=['POST'])
def send_invitation():
    try:
        data = request.json
        username = data.get('username')
        subtask_id = data.get('subtask_id')
        if not username or not subtask_id:
            return 'Invalid payload', 400

        invited_user = queries.get_user_by_username(username)
        # Return success if the user doesn't exists otherwise 
        # that would give away the username of other people, and if they are in the system
        if not invited_user:
            return jsonify('Invitation sent!'), 200

        if invited_user.id == current_user.id:
            return 'You cannot invite yourself', 400

        sent = queries.send_subtask_invitation(current_user, invited_user, subtask_id)
        if not sent:
            return 'Unable to send invitation', 400

    except Exception as e:
        print(e)
        return 'Error while sending invitation', 400
    return jsonify('Invitation sent!'), 200 


@user.route('/invitation_response', methods=['POST'])
def respond_invitation():
    try:
        todoist_key = decrypt_todoist_key()
        data = request.json
        invitation_id = data.get('invitation_id')
        accept = data.get('accept')

        if not isinstance(accept, bool) or not invitation_id:
            return 'Invalid payload', 400

        result = add_shared_subtask(current_user, todoist_key, invitation_id, accept)
        if not result:
            return 'Unable to respond to invitation', 400

    except Exception as e:
        print(e)
        return 'Error while sending invitation', 400
    return jsonify('Responded to invitation successfully!'), 200 