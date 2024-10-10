from flask import Blueprint, jsonify
from flask_login import current_user

import utils.session as session
from utils.settings import get_canvas_url
import utils.todoist as todoist

tasks = Blueprint('tasks', __name__)
BASE_URL = get_canvas_url()

# ENDPOINT: /api/v1/tasks

# Fetches assignments from Canvas and adds them to Todoist
@tasks.get('/update')
def update_tasks():
    
    canvas_token, todoist_token = session.decrypt_api_keys()
    todoist.add_missing_tasks(current_user.id, canvas_token, todoist_token)

    return jsonify({'success': True})
