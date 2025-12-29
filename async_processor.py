import logging
from queue import Queue
from threading import Thread
from agent import get_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

job_queue = Queue()

def worker():
    while True:
        file_path = job_queue.get()
        if file_path is None:
            logger.info("Worker shutting down")
            break
        try:
            logger.info(f"Processing file: {file_path}")
            get_response(file_path)
            logger.info(f"Successfully processed: {file_path}")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
        finally:
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