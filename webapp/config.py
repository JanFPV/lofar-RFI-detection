# webapp/config.py

# Simulated Data Configuration
USE_SIMULATED_DAT = True
SIMULATED_DAT_PATH = "test_data/fake_observation.dat"
SIMULATED_META_PATH = "test_data/observation.meta"

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
