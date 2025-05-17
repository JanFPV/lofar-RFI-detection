import threading
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lofarimaging.rfi_tools.realtime import read_blocks
from webapp import state, config

def start_observation():
    input_path = state.config["folder"]

    # NOTE: Output and temp directory are set to Flask's static folder for image visibility
    output_path = config.IMAGES_FOLDER
    temp_dir = output_path + "temp"

    step = state.config["step"]
    max_threads = state.config["threads"]

    def run():
        read_blocks(
            input_path=input_path,
            output_path=output_path,
            caltable_dir=config.CALTABLE_DIR,
            temp_dir=temp_dir,
            sleep_interval=config.SLEEP_INTERVAL,
            station_name=config.STATION_NAME,
            integration_time_s=config.INTEGRATION_TIME_S,
            rcu_mode=config.RCU_MODE,
            height=config.HEIGHT_METERS,
            step=step,
            max_threads=max_threads
        )

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


# NOTE: Output and temp directory are set to Flask's static folder for image visibility
# This allows the generated images to be displayed directly on the web interface.

# NOTE: Currently there is no stop mechanism – read_blocks runs in an infinite loop.
# To support stopping from the Flask UI, we will need to implement a shared flag (e.g., state.is_observing)
# and check it periodically inside the reading loop.

# NOTE: Discarded blocks (due to step filtering) are currently ignored.
# In the future, we may want to save them as .dat files for post-analysis.

# NOTE: Only one .dat file is processed at the moment.
# We could add support for detecting and switching to new files if needed (e.g., file rotation during observation).

# NOTE: There is no feedback about processing state (e.g., number of images processed).
# Adding counters or logs shown in the web UI could be useful for tracking progress.

# NOTE: Error handling is printed to the console only.
# In future versions, errors could be logged or shown in the web interface.
