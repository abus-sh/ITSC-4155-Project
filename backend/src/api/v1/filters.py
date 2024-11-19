from flask import Blueprint, request, Request, jsonify
from flask_login import current_user

import utils.queries as queries

filters = Blueprint('filters', __name__)


@filters.get('')
def get_filters():
    filters = queries.get_filters(current_user)

    return jsonify({'filters': filters}), 200


@filters.post('/new')
def create_filter():
    # Check that a value for the filter was provided.
    filter_str = _get_filter_name(request)
    if filter_str is None:
        return jsonify({'success': False, 'message': 'Missing or invalid filter.'}), 400

    if not queries.create_filter(current_user, filter_str):
        return jsonify({'success': False, 'message': 'An unknown error occurred.'}), 500

    return jsonify({'success': True, 'message': 'Created filter.'}), 200


@filters.delete('')
def delete_filter():
    # Check that a value for the filter was provided.
    filter_str = _get_filter_name(request)
    if filter_str is None:
        return jsonify({'success': False, 'message': 'Missing or invalid filter.'}), 400

    try:
        db_id = queries.delete_filter(current_user, filter_str)
        if db_id is None:
            return jsonify({'success': False, 'message': 'An unknown error occurred.'}), 500
    except ValueError:
        return jsonify({'success': False, 'message': 'Filter does not exist.'}), 404

    return jsonify({'success': True, 'message': 'Deleted filter.'}), 200


def _get_filter_name(request: Request) -> str | None:
    data = request.json

    if 'filter' not in data or type(data['filter']) is not str:
        return None

    filter_str: str = data['filter']
    if filter_str == '' or len(filter_str) > 50:
        return None

    return filter_str
