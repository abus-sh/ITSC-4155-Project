from flask import Blueprint, jsonify
from flask_login import current_user

import utils.session as session
from utils.settings import get_canvas_url, time_it
import utils.todoist as todoist

tasks = Blueprint('tasks', __name__)
BASE_URL = get_canvas_url()

# ENDPOINT: /api/v1/tasks

# Fetches assignments from Canvas and adds them to Todoist
@tasks.post('/update')
def update_tasks():
    try:
        canvas_token, todoist_token = session.decrypt_api_keys()
        with time_it("* Total time for adding Todoist Tasks: "):
            todoist.add_update_tasks(current_user.id, canvas_token, todoist_token)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        print('Error synching assignments to Todoist from Canvas: ', e)
        return jsonify({'success': False}), 400
