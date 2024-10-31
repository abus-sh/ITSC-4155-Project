from flask import Blueprint
from flask_login import login_required

from api.v1.courses import courses
from api.v1.tasks import tasks
from api.v1.user import user


api_v1 = Blueprint('api_v1', __name__)
api_v1.register_blueprint(courses, url_prefix='/courses')
api_v1.register_blueprint(user, url_prefix='/user')
api_v1.register_blueprint(tasks, url_prefix='/tasks')

# This means that individual routes don't need authentication protection. All childen routes will
# be protected.
@api_v1.before_request
@login_required
def ensure_authentication():
    pass
