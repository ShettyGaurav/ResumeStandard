import streamlit as st
import os
import logging
from pathlib import Path
from automate import start_watchdog
from async_processor import enqueue, start_worker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Helper functions

def save_sync(uploaded_file):
    path = os.path.join(INPUT_DIR, uploaded_file.name)
    logger.info(f"Saving file synchronously: {uploaded_file.name}")
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    logger.info(f"File saved to: {path}")
    return path

def save_async(uploaded_file):
    path = os.path.join(ASYNC_INPUT_DIR, uploaded_file.name)
    logger.info(f"Saving file for async processing: {uploaded_file.name}")
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    logger.info(f"File saved to: {path}")
    return path


if "async_started" not in st.session_state:
    logger.info("Starting async worker threads")
    start_worker(3)
    st.session_state.async_started = True
    logger.info("Async processing system initialized")


INPUT_DIR = "ResumeFolder"
OUTPUT_DIR = "OutputFolder"
ASYNC_INPUT_DIR = "ResumeFolderasync"

# Setup
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASYNC_INPUT_DIR, exist_ok=True)

st.set_page_config(page_title="Resume Processor", layout="wide")

# Start watchdog
if "watchdog_observer" not in st.session_state:
    st.session_state.watchdog_observer = start_watchdog()

# Header
st.title("Resume Processor")
st.success("System Active & Monitoring")

# Upload
st.subheader("Upload Files")
uploaded_files = st.file_uploader(
    "Drop PDF or DOCX files",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files)==1:
        logger.info(f"Single file upload - using sync processing: {uploaded_files[0].name}")
        save_sync(uploaded_files[0])
        st.success(f"Added: {uploaded_files[0].name}")
    else:
        logger.info(f"Multiple files upload - using async processing: {len(uploaded_files)} files")
        for file in uploaded_files:
            path = save_async(file)
            enqueue(path)
        st.success(f"Queued {len(uploaded_files)} files for processing")

# File Lists
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Queue")
    input_files = list(Path(INPUT_DIR).glob("*"))
    if not input_files:
        st.info("No files in queue")
    else:
        for file in input_files:
            st.write(f"📄 {file.name}")
            with open(file, "rb") as f:
                st.download_button(f"Download {file.name}", f, file.name, key=f"in-{file.name}")

with col2:
    st.subheader("Processed Files")
    output_files = list(Path(OUTPUT_DIR).glob("*"))
    if not output_files:
        st.info("No processed files yet")
    else:
        for file in output_files:
            st.write(f"✅ {file.name}")
            with open(file, "rb") as f:
                st.download_button(f"Download {file.name}", f, file.name, key=f"out-{file.name}")

if st.button("Refresh"):
    st.rerun()