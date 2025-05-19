# config.py

import getpass
username = getpass.getuser()

# Simulated Data Configuration
USE_SIMULATED_DAT = True
SIMULATED_DAT_PATH = f"/home/{username}/Documents/LV614_image_data/xst/20241119_210154_xst.dat"
SIMULATED_SUBBAND_MIN = 61
SIMULATED_SUBBAND_MAX = 182
SIMULATED_OUTPUT_PATH = "tmp/simulated_observation_xst.dat"


#SIMULATED_DAT_PATH = f"/home/{username}/Documents/LV614_image_data/xst/20241106_212920_xst.dat"
#SIMULATED_SUBBAND_MIN = 51
#SIMULATED_SUBBAND_MAX = 461

# Flask Server Configuration
FLASK_PORT = 5000
FLASK_HOST = "0.0.0.0"

# Paths
IMAGES_FOLDER = "webapp/static/images/"
LOG_PATH = "session_log.json"
CALTABLE_DIR = "CalTables/"

# Observation parameters
STATION_NAME = "LV614"
INTEGRATION_TIME_S = 2
RCU_MODE = 3
HEIGHT_METERS = 1.5
SLEEP_INTERVAL = 0.2

# Default runtime configuration
DEFAULT_OBSERVATION_CONFIG = {
    "folder": "/data",
    "threads": 4,
    "step": 1
}

# Warmup file
WARMUP_FILE = "./lofarimaging/rfi_tools/20230111_071514_xst.dat"
WARMUP_SUBBAND = 120
#WARMUP_OBSTIME =