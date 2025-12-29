import os
import hashlib
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_KEY"]

BUCKET = "ResumeBucket"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def upload_pdf(local_path: str, file_hash: str) -> str:
    if os.path.getsize(local_path) == 0:
        raise RuntimeError("PDF file is empty")

    name, _ = os.path.splitext(os.path.basename(local_path))

    safe_name = f"{name}_{file_hash[:12]}.pdf"
    remote_path = f"folder_in_bucket/{safe_name}"

    with open(local_path, "rb") as f:
        supabase.storage.from_(BUCKET).upload(
            path=remote_path,
            file=f,
            file_options={
                "content-type": "application/pdf",
                "upsert": False,  # 🔒 dedupe guarantee
            },
        )

    return remote_path


def list_files(folder: str):
    return supabase.storage.from_(BUCKET).list(folder)

def download_file(remote_path: str) -> None:
    data = supabase.storage.from_(BUCKET).download(remote_path)
    return data
    


def file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def output_exists(file_hash: str) -> bool:
    files = supabase.storage.from_(BUCKET).list("folder_in_bucket")
    return any(file_hash in f["name"] for f in files)
