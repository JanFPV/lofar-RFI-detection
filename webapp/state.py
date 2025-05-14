import os
import pandas as pd

# Estado de ejecución
is_observing = False

# Configuración activa
config = {
    "folder": "",
    "threads": 4,
    "step": 1
}

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
    if os.path.exists(path):
        image_log = pd.read_json(path)
    else:
        image_log = pd.DataFrame(columns=[
            "timestamp", "filename", "subband", "status", "duration", "frame_index"
        ])
