FROM python:3.10.12-bookworm

WORKDIR "/app"

RUN --mount=type=bind,source="./requirements.txt",target="/app/requirements.txt" \
    ["python3", "-m", "pip", "install", "-r", "requirements.txt"]
RUN ["python3", "-m", "pip", "install", "waitress==3.0.0"]

COPY "./src" "."

CMD ["waitress-serve", "--host", "0.0.0.0", "--port", "5000", "app:app"]
