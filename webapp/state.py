# webapp/state.py

import os
import pandas as pd
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config as app_config

# Estado de ejecución
is_observing = False

# Configuración activa
config = app_config.DEFAULT_OBSERVATION_CONFIG.copy()

# Log de imágenes procesadas (aunque esté vacío al principio)
image_log = pd.DataFrame(columns=[
    "timestamp", "filename", "subband", "status", "duration", "frame_index"
])

def add_image_entry(filename, subband, status="processed", duration=None, frame_index=None):
    global image_log
    image_log.loc[len(image_log)] = [
        pd.Timestamp.utcnow().isoformat(),
        filename,
        subband,
        status,
        duration,
        frame_index
    ]

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
