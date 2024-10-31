from flask import Blueprint, jsonify, request
from flask_login import current_user

import utils.session as session
import utils.todoist as todoist
from utils.settings import get_canvas_url

from utils.queries import get_subtasks_for_tasks, TaskStatus


tasks = Blueprint('tasks', __name__)
BASE_URL = get_canvas_url()

# ENDPOINT: /api/v1/tasks

# Fetches assignments from Canvas and adds them to Todoist
@tasks.post('/update')
def update_tasks():
    canvas_token, todoist_token = session.decrypt_api_keys()
    try:
        todoist.add_update_tasks(current_user.id, canvas_token, todoist_token)
    except Exception as e:
        print('Error synching assignments to Todoist from Canvas: ', e)
        return jsonify({'success': False}), 400

    try:
        todoist.sync_task_status(current_user, todoist_token)
    except Exception as e:
        """ print('Error updating task completion') """
        raise e
        return jsonify({'success': False}), 400

    return jsonify({'success': True}), 200

@tasks.post('/add_subtask')
def add_subtask_user():
    try:
        todoist_token = session.decrypt_todoist_key()
        data = request.json
        
        canvas_id = data.get('canvas_id')
        subtask_name = data.get('name').strip()
        subtask_desc = data.get('description')
        subtask_status = TaskStatus.from_integer(data.get('status'))
        subtask_date = data.get('due_date')
        
        if not canvas_id or not subtask_name or not subtask_status:
            return jsonify({'success': False, 'message': 'Invalid subtask parameters'}), 400
        
        result = todoist.add_subtask(current_user, todoist_token, canvas_id, subtask_name, subtask_desc, 
                                subtask_status, subtask_date)
        if result:
            return jsonify({'success': True, 'id': result}), 200
        else:
            return jsonify({'success': False, 'message':'Failed to create subtask'}), 400 
    except Exception as e:
        print('Error adding a subtask: ', e)
        return jsonify({'success': False, 'message':'Unable to create subtask'}), 400
    
@tasks.post('/get_subtasks')
def get_subtasks():
    try:
        data = request.json
        task_ids = data.get('task_ids')
        
        if task_ids and isinstance(task_ids, list):
            subtasks = get_subtasks_for_tasks(current_user, task_ids)
            return jsonify(subtasks), 200
        
        elif len(task_ids) == 0:
            return jsonify({'success': False, 'message':'No IDs were provided'}), 400

    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message':'Error while getting subtasks'}), 400
    return jsonify({'success': False, 'message':'Unable to get subtasks'}), 404

@tasks.post('/<task_id>/close')
def close_task(task_id: str):
    todoist_token = session.decrypt_todoist_key()
    result = todoist.close_task(current_user, todoist_token, task_id)
    if result:
        return jsonify({'success': True, 'message': f'{task_id} closed'})
    return jsonify({'success': False, 'message': f'Unable to close {task_id}'}), 400


@tasks.post('/<task_id>/open')
def open_task(task_id: str):
    todoist_token = session.decrypt_todoist_key()
    result = todoist.open_task(current_user, todoist_token, task_id)
    if result:
        return jsonify({'success': True, 'message': f'{task_id} opened'})
    return jsonify({'success': False, 'message': f'Unable to open {task_id}'}), 400


@tasks.post('/<task_id>/toggle')
def toggle_task(task_id: str):
    todoist_token = session.decrypt_todoist_key()
    result = todoist.toggle_task(current_user, todoist_token, task_id)
    if result:
        return jsonify({'success': True, 'message': f'{task_id} toggled'})
    return jsonify({'success': False, 'message': f'Unable to open {task_id}'}), 400
