import streamlit as st
import os
from pathlib import Path
from automate import start_watchdog
from async_processor import enqueue, start_worker


# Helper functions

def save_sync(uploaded_file):
    path = os.path.join(INPUT_DIR, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def save_async(uploaded_file):
    path = os.path.join(ASYNC_INPUT_DIR, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


if "async_started" not in st.session_state:
    start_worker(3)
    st.session_state.async_started = True


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
        save_sync(uploaded_files[0])
    else:
        for file in uploaded_files:
            path = save_async(file)
            enqueue(path)

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