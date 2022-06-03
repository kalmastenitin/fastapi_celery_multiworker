from celery import Celery
import os
import queue
import time
from kombu import Exchange, Queue
import fnmatch
import cv2
import ffmpeg
from pathlib import Path

celery = Celery("tasks", broker="redis://localhost:6379",
                backend="db+mysql+pymysql://root:toolkitsecret@mysql-server:3306/task")
celery.conf.broker_url = os.environ.get(
    "CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "db+mysql+pymysql://root:toolkitsecret@mysql-server:3306/task")

celery.conf.worker_max_tasks_per_child = 2
celery.conf.task_queues = [
    Queue('default', Exchange('default'), routing_key='default',
          queue_arguments={'x-max-priority': 10}),
    Queue('priority_high', Exchange('priority_high'), routing_key='priority_high',
          queue_arguments={'x-max-priority': 1}),
]

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='Europe/Oslo',
    enable_utc=True,
)


@celery.task(name="create_task", bind=True, queue="default", priority=10, rate_limit='1/m')
def create_task(self, task_type):
    self.update_state(state="PROCESSING")
    for i in range(10):
        time.sleep(int(task_type))
    self.update_state(state="COMPLETED")
    return True


@celery.task(name="create_task_priority", bind=True, queue="priority_high", priority=1, rate_limit='10/m')
def create_task_priority(self, task_type):
    self.update_state(state="PROCESSING")
    for i in range(10):
        time.sleep(int(task_type))
    self.update_state(state="COMPLETED")
    return True


@celery.task(name="data_cleaning", bind=True, queue="default", priority=10, rate_limit='1/m')
def data_cleaning(self, body):
    wd = range(320, 2048)
    ht = range(240, 1536)
    new_size = 320, 240
    image_count = body["image_count"]
    exts = ('*.jpeg', '*.JPEG', '*.png', '*.PNG', '*.jpg', '*.JPG')
    files = [f.path for f in os.scandir(body["path"]) if any(
        fnmatch.fnmatch(f, p) for p in exts)]
    total_files = len(files)
    count = 0
    for file in sorted(files):
        try:
            img = cv2.imread(file)
            he = img.shape[0]
            wi = img.shape[1]
            if he in ht:
                if wi in wd:
                    try:
                        process = (
                            ffmpeg
                            .input(Path(file))
                            .filter("scale", width=new_size[0], height=new_size[1])
                            .output(f'{body["temp"]}/{body["projectname"]}_{image_count}.jpg')
                            .overwrite_output()
                            .run(quiet=True)
                        )
                    except Exception as e:
                        image = cv2.imread(file)
                        size = (new_size[0], new_size[1])
                        resize = cv2.resize(image, size)
                        cv2.imwrite(
                            f'{body["temp"]}/{body["projectname"]}_{image_count}.jpg', resize)
                        continue

        except Exception as e:
            print(e, file)
        count += 1
        image_count += 1
        self.update_state(state='PROGRESS',
                          meta={'current': count, 'total': total_files, "percent": (count/total_files)*100})
    return {'current': count, 'total': total_files, "percent": (count/total_files)*100}
