from queue import Queue
from threading import Thread

from agent import get_response


job_queue = Queue()

def worker():
    while True:
        file_path = job_queue.get()
        if file_path is None:
            break
        try:
            get_response(file_path)
        finally:
            job_queue.task_done()

def start_worker(count=3):
    for _ in range(count):
        Thread(target=worker,daemon=True).start()
def enqueue(file_path):
    job_queue.put(file_path)