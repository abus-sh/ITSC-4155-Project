# ITSC 4155 Project
This is a final project for ITSC 4155. It integrates with Canvas and Todoist to automatically add
action items from courses in Canvas to Todoist as tasks.

## Local Development
To run the frontend locally, you must have Node 20 installed and install the packages described by
`frontend/package.json`. From there, you can run `ng serve` in `frontend` to start the frontend on
http://127.0.0.1:4200.

To run the backend locally, you must have Python 3.10 installed and install the modules described by
`backend/requirements.txt`. If you wish to run unit tests, you must also install the modules
described by `backend/requirements-dev.txt`. From there, you can run `python3 -m flask run` in
`backend/src` to start the backend on http://127.0.0.1:5000/.

## Deployment
This project can be deployed with Docker Compose. By default, the frontend is exposed on port 4200
and the backend is exposed on port 5000. The files in the "util" directory can be used to
automatically update the project on new commits to main. The steps to do this are:

1. Install `update-repo.service` and `update-repo.timer` to `/etc/systemd/system`.
2. Enable and start `update-repo.timer`.
3. In the `secrets` directory, supply a certificate named `site.crt` and a key named `site.key`.

From there, the repo will be updated every minute. If there is a change, the Docker images will be
rebuilt and redeployed.
