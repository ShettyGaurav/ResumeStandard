import streamlit as st
import os
import logging
from pathlib import Path
from async_processor import enqueue, start_worker
from checksupabase import list_files, download_file

# ---------------- LOGGING ----------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------- CONFIG ----------------

INPUT_DIR = "ResumeFolder"              # sync input (watchdog)
ASYNC_INPUT_DIR = "ResumeFolderasync"   # async input (queue)
SUPABASE_FOLDER = "folder_in_bucket"    # processed resumes in Supabase

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(ASYNC_INPUT_DIR, exist_ok=True)

# ---------------- HELPERS ----------------

def save_sync(uploaded_file):
    path = os.path.join(INPUT_DIR, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    logger.info(f"Saved sync file: {path}")
    return path


def save_async(uploaded_file):
    path = os.path.join(ASYNC_INPUT_DIR, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    logger.info(f"Saved async file: {path}")
    return path


# ---------------- STREAMLIT INIT ----------------

st.set_page_config(page_title="Resume Processor", layout="wide")

# Start async workers ONCE
if "async_started" not in st.session_state:
    logger.info("Starting async workers")
    start_worker(3)
    st.session_state.async_started = True

# ---------------- UI ----------------

st.title("📄 Resume Processor")
st.success("System Active & Monitoring")

# ---------------- UPLOAD ----------------

st.subheader("Upload Files")

uploaded_files = st.file_uploader(
    "Drop PDF or DOCX files",
    type=["pdf", "docx"],
    accept_multiple_files=True,
)

if uploaded_files:
    # Track processed files to prevent re-processing on refresh
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = set()
    
    # Get file identifiers (name + size)
    current_files = {(f.name, f.size) for f in uploaded_files}
    new_files = [f for f in uploaded_files if (f.name, f.size) not in st.session_state.processed_files]
    
    if new_files:
        if len(new_files) == 1:
            file = new_files[0]
            save_sync(file)
            st.success(f"Added for sync processing: {file.name}")
        else:
            for file in new_files:
                path = save_async(file)
                enqueue(path)
            st.success(f"Queued {len(new_files)} files for async processing")
        
        # Mark these files as processed
        st.session_state.processed_files.update(current_files)

# ---------------- FILE LISTS ----------------

col1, col2 = st.columns(2)

# -------- INPUT QUEUE (LOCAL / SYNC) --------
with col1:
    st.subheader("Input Queue (Sync)")
    input_files = list(Path(INPUT_DIR).glob("*"))

    if not input_files:
        st.info("No files in sync queue")
    else:
        for file in input_files:
            st.write(f"📄 {file.name}")
            with open(file, "rb") as f:
                st.download_button(
                    f"Download {file.name}",
                    f,
                    file.name,
                    key=f"in-{file.name}",
                )

# -------- PROCESSED FILES (SUPABASE) --------
with col2:
    st.subheader("Processed Files (Supabase)")

    try:
        files = list_files(SUPABASE_FOLDER)

        # ✅ Correct filtering: keep only real files
        files = [
            f for f in files
            if f.get("name") and f.get("metadata") is not None
        ]

        if not files:
            st.info("No processed files yet")
        else:
            for file in files:
                name = file["name"]
                remote_path = f"{SUPABASE_FOLDER}/{name}"

                st.write(f"✅ {name}")

                file_bytes = download_file(remote_path)

                st.download_button(
                    label=f"Download {name}",
                    data=file_bytes,
                    file_name=name,
                    mime="application/pdf",
                    key=f"supabase-{name}",
                )

    except Exception as e:
        st.error(f"Failed to fetch processed files: {e}")

# ---------------- REFRESH ----------------

if st.button("Refresh"):
    st.rerun()
