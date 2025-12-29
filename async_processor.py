import logging
from queue import Queue

from threading import Thread,Lock
from agent import get_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

job_queue = Queue()
processing = set()
lock = Lock()


def worker():
    while True:
        file_path = job_queue.get()
        if file_path is None:
            break

        with lock:
            if file_path in processing:
                job_queue.task_done()
                continue
            processing.add(file_path)

        try:
            get_response(file_path)
        finally:
            with lock:
                processing.remove(file_path)
            job_queue.task_done()


def start_worker(count=3):
    logger.info(f"Starting {count} async workers")
    for i in range(count):
        thread = Thread(target=worker, daemon=True)
        thread.start()
        logger.info(f"Started worker thread {i+1}")

def enqueue(file_path):
    logger.info(f"Enqueuing file for processing: {file_path}")
    job_queue.put(file_path)