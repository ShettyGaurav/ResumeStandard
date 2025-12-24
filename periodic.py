import hashlib
import os
from agent import get_response
FILE_HASHES = {}  # persists in-memory while process runs

def get_file_hash(path):
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def periodic_scan():
    print("[SCHEDULER] Scanning folder for changes")

    for filename in os.listdir(INPUT_DIR):
        path = os.path.join(INPUT_DIR, filename)

        if not path.lower().endswith((".pdf", ".docx", ".jpg")):
            continue

        current_hash = get_file_hash(path)
        previous_hash = FILE_HASHES.get(path)

        if current_hash != previous_hash:
            FILE_HASHES[path] = current_hash
            print(f"[CHANGE DETECTED] {path}")
            get_response(path)

periodic_scan()
