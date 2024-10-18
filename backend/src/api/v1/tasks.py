from flask import Blueprint, jsonify, request
from flask_login import current_user

import utils.session as session
import utils.todoist as todoist
from utils.settings import get_canvas_url, time_it

from utils.queries import create_subtask, SubStatus


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

@tasks.post('/add_subtask')
def add_subtask():
    try:
        #canvas_token, todoist_token = session.decrypt_api_keys()
        data = request.json
        
        task_id = data.get('task_id')
        subtask_name = data.get('name')
        subtask_desc = data.get('description')
        subtask_status = SubStatus.from_integer(data.get('status'))
        subtask_date = data.get('due_date')
        
        if not task_id or not subtask_name or not subtask_status:
            return jsonify({'success': False, 'message': 'Invalid subtask parameters'}), 400
        
        result = create_subtask(current_user, task_id, subtask_name, subtask_desc, 
                                subtask_status, subtask_date)
        if result:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message':'Failed to create subtask'}), 400 
    except Exception as e:
        print('Error adding a subtask: ', e)
        return jsonify({'success': False, 'message':'Unable to create subtask'}), 400