# Asynchronous Tasks with FastAPI and Celery

Example of how to handle background processes with FastAPI, Celery, and Docker.

## Want to learn how to build this?

docker-compose up -d --build

## Want to use this project?


Open your browser to [http://localhost:8000/api/docs](http://localhost:8000/api/docs) to view the app or to [http://localhost:5556](http://localhost:5556) to view the Flower dashboard.

Trigger a new task:

user /api/tasks - for normal task
user /api/priority_tasks - for priority task with multiple worker

Use Swagger

