# webapp/state.py

import os
import pandas as pd
import numpy as np
import threading
import datetime
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config as app_config

# Execution state
is_observing = False
shutdown_requested = False
system_status = "Idle"  # "Running", "Stopping...", "Idle"

# Active configuration
config = app_config.DEFAULT_OBSERVATION_CONFIG.copy()

# Processed images log
image_log = pd.DataFrame(columns=[
    "timestamp", "filename", "subband", "status", "duration", "frame_index"
])

# System state for the web interface
last_block = 0
last_subband = None
processing_times = []
current_dat_file = ""
subband_range = (None, None)
pending_tasks = 0
pending_lock = threading.Lock()

def add_image_entry(filename, subband, status="processed", duration=None, frame_index=None, timestamp=None):
    global image_log, last_subband
    last_subband = subband

    if timestamp is None:
        timestamp = datetime.datetime.utcnow()

    image_log.loc[len(image_log)] = [
        timestamp,
        filename,
        subband,
        status,
        duration,
        frame_index
    ]

def get_status():
    avg_time = round(np.mean(processing_times[-10:]), 2) if processing_times else 0
    return {
        "status": system_status,
        "last_block": last_block,
        "last_subband": last_subband,
        "pending_threads": pending_tasks,
        "avg_processing_time": avg_time,
        "current_dat_file": current_dat_file,
        "subband_range": subband_range,
        "threads": config.get("threads", None),
        "step": config.get("step", None)
    }

def save_log(path="webapp/session_log.json"):
    image_log.to_json(path, orient="records", indent=2)


def load_log(path="webapp/session_log.json"):
    global image_log
    if os.path.exists(path) and os.path.getsize(path) > 0:
        try:
            image_log = pd.read_json(path)
        except ValueError:
            print("session_log.json is invalid or empty. Reinitializing log.")
            image_log = pd.DataFrame(columns=[
                "timestamp", "filename", "subband", "status", "duration", "frame_index"
            ])
    else:
        print("session_log.json not found or empty. Initializing empty log.")
        image_log = pd.DataFrame(columns=[
            "timestamp", "filename", "subband", "status", "duration", "frame_index"
        ])
