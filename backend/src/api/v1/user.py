from canvasapi import Canvas
from flask import Blueprint, jsonify, request

from api.auth.authentication import decrypt_canvas_key
from utils.settings import get_canvas_url


user = Blueprint('user', __name__)
BASE_URL = get_canvas_url()


# Get missing submissions for active courses (past the due date)
@user.route('/missing_submissions', methods=['GET', 'POST'])
def get_missing_submissions():
    canvas_key = decrypt_canvas_key()

    try:
        canvas = Canvas(BASE_URL, canvas_key)
        # get courses ids from request json body
        request_data = request.get_json(silent=True)
        courses_list = request_data.get('course_ids', [])
        # If the course_ids were not provided, fetch them from the active enrollment canvas api
        if len(courses_list) <= 0:
            current_courses = canvas.get_courses(enrollment_state='active')
            for course in current_courses:
                one_course = getattr(course, 'id', None)
                if one_course is not None:
                    courses_list.append(one_course)

        missing_submissions = canvas.get_current_user().get_missing_submissions(course_ids=courses_list)
        miss_assignments_list = []
        for assignment in missing_submissions:
            fields = [
                'id', 'name', 'description', 'due_at','course_id', 'html_url', 
            ]
            miss_assignment = {field: getattr(assignment, field, None) for field in fields}
            miss_assignments_list.append(miss_assignment)
    except Exception as e:
        return 'Unable to make request to Canvas API', 400
    except AttributeError as e:
        return 'Unable to get field for courses', 404
    return jsonify(miss_assignments_list), 200

# TO DO:
# GET /api/v1/users/:id/graded_submissions (Get a users most recently graded submissions)
