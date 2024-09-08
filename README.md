# ITSC 4155 Project
This is a final project for ITSC 4155. It integrates with Canvas and Todoist to automatically add
action items from courses in Canvas to Todoist as tasks.

## Deployment
This project can be deployed with Docker Compose. By default, the frontend is exposed on port 4200
and the backend is exposed on port 5000. The files in the "util" directory can be used to
automatically update the project on new commits to main. The steps to do this are:

1. Install `update-repo.service` and `update-repo.timer` to `/etc/systemd/system`.
2. Enable and start `update-repo.timer`.

From there, the repo will be updated every minute. If there is a change, the Docker images will be
rebuilt and redeployed.