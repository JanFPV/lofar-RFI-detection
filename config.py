# config.py

import getpass
username = getpass.getuser()

# Configuration for simulated observation
if username != "oper":
    SIMULATED_DAT_PATH = f"/home/{username}/Documents/LV614_image_data/20250521_070907_xst.dat"
    SIMULATED_OUTPUT_PATH = "tmp/simulated_observation_xst.dat"
else:
    SIMULATED_DAT_PATH = f"/mnt/LOFAR0/xst/20241119_210154_xst.dat"
    SIMULATED_OUTPUT_PATH = "/mnt/LOFAR0/erasmus_2025/simulated_observation_xst.dat"

SIMULATED_SUBBAND_MIN = 51
SIMULATED_SUBBAND_MAX = 461

# Flask Server Configuration
FLASK_PORT = 5000
FLASK_HOST = "0.0.0.0"

# Paths
IMAGES_FOLDER = "webapp/static/images/"
LOG_PATH = "session_log.json"
CALTABLE_DIR = "CalTables/"
LOG_PATH = "webapp/static/images/server.log"

# Observation parameters
STATION_NAME = "LV614"
INTEGRATION_TIME_S = 2
RCU_MODE = 3
SLEEP_INTERVAL = 0.2
MANUAL_SUBBANDS = False
MIN_SUBBAND = 200
MAX_SUBBAND = 200

# Default runtime configuration
DEFAULT_OBSERVATION_CONFIG = {
    "folder": "/data",
    "threads": 8,
    "step": 4,
    "height_m": 1.5,
    "extent": 150,
}

# Warmup file
WARMUP_FILE = "./lofarimaging/rfi_tools/20230111_072042_xst.dat"
WARMUP_SUBBAND = 284
