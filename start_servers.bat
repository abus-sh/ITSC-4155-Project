@echo off

:: Set the current directory to where the .bat file is located
cd /d %~dp0

:: Open a new command prompt and start the Flask server
start cmd /k "cd backend\src && py app.py"

:: Open a new command prompt and start the Angular server
start cmd /k "cd frontend && ng serve"
