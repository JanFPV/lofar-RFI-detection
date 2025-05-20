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

def save_log(path=None):
    global observation_path
    if path is None:
        if observation_path:
            path = os.path.join(observation_path, "session_log.json")
        else:
            path = "webapp/session_log.json"  # fallback por seguridad

    image_log.to_json(path, orient="records", indent=2)
    print(f"[LOG] Saved session log to {path}")


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


def load_all_logs_by_observation(base_dir="webapp/static/images"):
    logs_by_observation = {}

    for folder in os.listdir(base_dir):
        obs_path = os.path.join(base_dir, folder)
        log_path = os.path.join(obs_path, "session_log.json")

        if os.path.isdir(obs_path) and os.path.isfile(log_path):
            try:
                log_df = pd.read_json(log_path)
                logs_by_observation[folder] = log_df
                print(f"[LOG] Loaded log for observation {folder} ({len(log_df)} entries)")
            except Exception as e:
                print(f"[WARNING] Could not load log from {log_path}: {e}")

    return logs_by_observation


observation_path = None

def create_observation_directory(base_dir="webapp/static/images"):
    global observation_path
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    observation_path = os.path.join(base_dir, timestamp)

    os.makedirs(os.path.join(observation_path, "blocks"), exist_ok=True)
    os.makedirs(os.path.join(observation_path, "images"), exist_ok=True)
    os.makedirs(os.path.join(observation_path, "movies"), exist_ok=True)

    print(f"[SETUP] Created observation directory at {observation_path}")
