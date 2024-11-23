from flask import request, abort, session, redirect, render_template_string, Blueprint
from flask_login import current_user
from utils.settings import generate_random_string, get_frontend_url
import os
import requests


# Todoist OAuth 2.0 Secret
TODOIST_CLIENT = os.environ.get('TODOIST_CLIENT', '033c2a73ad3347609e9cf6ed1b0cd3fa')
#
# ATTENTION: To make it easier to run the application locally for the grading,
# the secret is stored in an accessible file. This is not recommended and will not be used for production.
#
with open(os.environ.get('TODOIST_SECRET', '../../secrets.example/todoist_secret.txt'), 'r') as file:
    TODOIST_SECRET = file.readline().strip()


todoist = Blueprint('todoist', __name__)


# Redirect to Todoist for giving permission
@todoist.route('/redirect', methods=['GET', 'POST'])
def give_todoist_permission():
    if current_user.is_authenticated:
        abort(401, "User is already authenticated.")

    auth_url = "https://todoist.com/oauth/authorize"
    scope = "data:read_write,data:delete"
    auth_state = generate_random_string(length=20)

    # Save state string in session to check that it's the same when redirected back
    session['oauth_state'] = auth_state

    # Ensure the redirect URL is properly constructed
    redirect_url = f"{auth_url}?client_id={TODOIST_CLIENT}&scope={scope}&state={auth_state}"

    return redirect(redirect_url)


@todoist.route('/get_token_info', methods=['GET'])
def exchange_token_route():
    if current_user.is_authenticated:
        abort(401, "User is already authenticated.")

    # Retrieve query parameters
    auth_code = request.args.get('code')
    auth_state = request.args.get('state')

    # If there aren't any arguments, reset the oath_state
    if not auth_code or not auth_state:
        session.pop('oauth_state')
        abort(400, "Couldn't get authorization arguments.")

    # Session with the auth state encrypted in the cookie will delete itself when all the website
    # tabs are closed (register page)
    session.permanent = True

    # Close the popup window and give focus back to the register page
    # Arguments are sent back to the registration page
    return render_template_string('''
    <html>
    <head>
        <title>Token Retrieved</title>
        <script type="text/javascript">
            // Post a message to the opener window (the register page)
            if (window.opener) {
                const authData = { result: "success", code: "{{ auth_code }}", state: "{{ auth_state }}" };
                window.opener.postMessage(authData, "{{ frontend_register }}");
            }
            window.close();
        </script>
    </head>
    <body>
        <h1>Args successfully retrieved!</h1>
        <p>You can close this window. </p>
    </body>
    </html>
    ''',  # noqa: E501
    auth_code=auth_code, auth_state=auth_state,  # noqa: E128
    frontend_register=get_frontend_url() + '/register')  # noqa: E128


#################################################################
#                                                               #
#                         EXCHANGE TOKEN                        #
#                                                               #
#################################################################

def exchange_token(code: str, state: str, session):
    stored_state = session.pop('oauth_state', None)

    if not code or not state or not stored_state or state != stored_state:
        return None

    todoist_token_url = 'https://todoist.com/oauth/access_token'
    body = {
        'client_id': TODOIST_CLIENT,
        'client_secret': TODOIST_SECRET,
        'code': code
    }
    response = requests.post(todoist_token_url, data=body)
    response_data = response.json()

    if response_data.get('error'):

        return None
    else:
        access_token = response_data.get('access_token')     # Access token
        token_type = response_data.get('token_type')         # Bearer
        return (token_type, access_token)
