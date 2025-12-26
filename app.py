import streamlit as st
import os
import threading
from pathlib import Path
import time
from automate import start_watchdog  # ✅ Import non-blocking starter

# ---------------- CONFIG ----------------

INPUT_DIR = "ResumeFolder"
OUTPUT_DIR = "OutputFolder"
VALID_EXTS = (".pdf", ".docx")

# ---------------- SETUP ----------------

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.set_page_config(page_title="Resume Processor", layout="wide")
st.title("📁 Resume Folder Processor")
st.caption("Upload folders or files · Auto-processed via LangGraph")

# ---------------- START WATCHDOG (ONCE) ----------------

if "watchdog_observer" not in st.session_state:
    st.session_state.watchdog_observer = None

if st.session_state.watchdog_observer is None:
    st.session_state.watchdog_observer = start_watchdog()
    st.success("✅ Background processor started!")

# ---------------- STATUS ----------------

st.subheader("🟢 Background Processor Status")
st.success("automate.py is running")

# ---------------- UPLOAD SECTION ----------------

st.divider()
st.subheader("⬆️ Upload Folder or Files")

uploaded_files = st.file_uploader(
    "Upload a folder (or multiple files)",
    type=["pdf", "docx"],
    accept_multiple_files=True,
)

if uploaded_files:
    for file in uploaded_files:
        filename = os.path.basename(file.name)
        dest_path = os.path.join(INPUT_DIR, filename)

        with open(dest_path, "wb") as f:
            f.write(file.getbuffer())
    
        st.success(f"Added: {filename}")
    # runThread() # Removed: Watchdog is already running in background
    st.info("Files stored in ResumeFolder. Processing will begin automatically.")

# ---------------- INPUT FILES ----------------

st.divider()
st.subheader("📂 Input Files (ResumeFolder)")

input_files = sorted(Path(INPUT_DIR).glob("*"))

if not input_files:
    st.warning("No input files found.")
else:
    print("Got input files")
    for file in input_files:
        col1, col2 = st.columns([4, 1])
        col1.text(file.name)

        with col2:
            with open(file, "rb") as f:
                st.download_button(
                    "⬇️ Download",
                    f,
                    file.name,
                    key=f"in-{file.name}",
                )

# ---------------- OUTPUT FILES ----------------

st.divider()
st.subheader("📂 Output Files (OutputFolder)")

output_files = sorted(Path(OUTPUT_DIR).glob("*"))

if not output_files:
    st.warning("No output files yet.")
else:
    for file in output_files:
        col1, col2 = st.columns([4, 1])
        col1.text(file.name)

        with col2:
            with open(file, "rb") as f:
                st.download_button(
                    "⬇️ Download",
                    f,
                    file.name,
                    key=f"out-{file.name}",
                )

# ---------------- MANUAL REFRESH ----------------

st.divider()
if st.button("🔄 Refresh Output Folder"):
    st.rerun()

st.caption("Watchdog monitors ResumeFolder · LangGraph pipeline runs automatically")
