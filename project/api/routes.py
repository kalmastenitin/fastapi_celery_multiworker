from fastapi import APIRouter, Body
from celery.result import AsyncResult
from fastapi.responses import JSONResponse

from worker import create_task, create_task_priority, data_cleaning
from worker import celery
import os

router = APIRouter()


@router.post("/tasks", status_code=201)
def run_task(interval: int):
    task = create_task.delay(interval)
    return JSONResponse({"task_id": task.id})


@router.post("/priority_tasks", status_code=201)
def run_task(interval: int):
    task = create_task_priority.delay(interval)
    return JSONResponse({"task_id": task.id})


@router.post("/data_clean", status_code=201)
def run_task(projectname: str):
    project_path = os.path.join(os.getcwd(), "workspace", f"{projectname}")
    os.mkdir(project_path)
    task = data_cleaning.delay(
        {"path": os.path.join(os.getcwd(), "workspace", "tmp"), "temp": project_path, "projectname": projectname, "image_count": 0})
    print(task.result)
    return JSONResponse({"task_id": task.id})


@router.get("/check_path")
def check_path():
    print(dir(celery.conf))
    temp_path = os.path.join(os.getcwd(), "workspace", "tmp")
    if os.path.exists(temp_path):
        return JSONResponse({"message": "success"})
    else:
        return JSONResponse({"message": "failed"}, status_code=400)


@router.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)


@router.get("/all")
def get_all_tasks():
    print(dir(celery.control.inspect()))
    print(celery.control.inspect().active_queues())
    print(celery.control.inspect().reserved())
    print(celery.control.inspect().stats())
    print(celery.control.inspect().registered())
    i = celery.control.inspect().active()
    # i = celery.control.inspect().revoked()
    print(i)
    return JSONResponse(i)


@router.delete("/task/{task_id}")
def remove_task_from_queue(task_id: str):
    celery.control.terminate(task_id)
    return JSONResponse(task_id)
