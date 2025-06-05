from celery import Celery
import os

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def process_file(filename):
    with open(filename, "r") as f:
        data = f.read()
    return f"Processed {filename}: {len(data)} bytes"
