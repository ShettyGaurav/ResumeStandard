from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
from agent import get_response

INPUT_DIR = "ResumeFolder"
OUTPUT_DIR = "OutputFolder"


class ResumeFolderHandler(FileSystemEventHandler):
    processed_files = set()

    def on_created(self, event):
        if event.is_directory:
            return

        if not event.src_path.lower().endswith((".pdf", ".docx")):
            return

        if event.src_path in self.processed_files:
            return

        self.processed_files.add(event.src_path)

        print(f"Processing: {event.src_path}")
        get_response(event.src_path)

    def process(self, file_path, event_type):
        if not file_path.lower().endswith((".pdf", ".docx")):
            return
        print(f"File Detected{file_path}")
        get_response(file_path)


def main():
    event_handler = ResumeFolderHandler()
    observer = Observer()
    observer.schedule(event_handler, INPUT_DIR, recursive=False)
    print(f"[INFO] Watching folder: {INPUT_DIR}")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
