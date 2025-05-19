# lofarimaging/rfi_tools/realtime.py

import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
import time
import os
import datetime
import tempfile
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lofarimaging import get_station_type, rcus_in_station, make_xst_plots, read_acm_cube
from webapp import state
import config


__all__ = [
    "wait_for_dat_file",
    "read_blocks",
    "obs_parser",
    "get_subbands",
]

def warmup_processing():
    station_name=config.STATION_NAME
    rcu_mode=config.RCU_MODE
    height=config.HEIGHT_METERS
    caltable_dir=config.CALTABLE_DIR

    def _run():
        try:
            start_time = time.time()
            print("Starting warmup image generation...")
            with tempfile.TemporaryDirectory() as temp_dir:
                #print(f"Using temp path: {temp_dir}")
                station_type = get_station_type(station_name)
                num_rcu = rcus_in_station(station_type)

                with open(config.WARMUP_FILE, "rb") as f:
                    block = np.fromfile(f, dtype=np.complex128).reshape((num_rcu, num_rcu))

                #timestamp = config.WARMUP_OBSTIME
                timestamp = datetime.datetime.now()
                subband = config.WARMUP_SUBBAND

                _, _, _ = make_xst_plots(
                    block, station_name, timestamp, subband, rcu_mode,
                    map_zoom=18, outputpath=temp_dir, mark_max_power=True,
                    height=height, return_only_paths=True, caltable_dir=caltable_dir
                )
            duration = time.time() - start_time
            print(f"Warmup image generated in {duration:.2f} seconds.")
        except Exception as e:
            #import traceback
            #print("Warmup failed:")
            #traceback.print_exc()
            print(f"Warmup failed: {e}")

    threading.Thread(target=_run, daemon=True).start()


def wait_for_dat_file(input_path, sleep_interval=0.2):
    print(f"Waiting for a .dat file in {input_path}...")
    while True:
        files = [f for f in os.listdir(input_path) if f.endswith("_xst.dat")]
        if files:
            return os.path.join(input_path, files[0])  # Return first .dat file found
        time.sleep(sleep_interval)


def read_blocks(input_path, output_path, caltable_dir, temp_dir, sleep_interval, station_name, integration_time_s, rcu_mode, height, step=1, max_threads=4):
    # Get station type and number of RCU channels based on name
    station_type = get_station_type(station_name)
    num_rcu = rcus_in_station(station_type)
    block_size = num_rcu * num_rcu

    # Wait until a .dat file appears in the input path
    filename = wait_for_dat_file(input_path)
    print(f"File {filename} detected.")
    print(f"Starting real-time block reader...")

    # Buffer to accumulate streamed data
    buffer = np.array([], dtype=np.complex128)

    block_counter = 0      # Counts total blocks seen
    subband_counter = 0    # Tracks current subband for image labeling

    # Read min/max subbands from metadata file
    min_subband, max_subband = get_subbands(input_path)

    pending_tasks = 0
    pending_lock = threading.Lock()

    def process_block_wrapper(block, subband, timestamp):
        try:
            process_block(block, subband, timestamp)
        finally:
            with pending_lock:
                nonlocal pending_tasks
                pending_tasks -= 1


    # Function executed by worker threads to generate images
    def process_block(block, subband, timestamp):
        try:
            start_time = time.time()
            print(f"Processing subband {subband} at {timestamp}")
            sky_img, nf_img, _ = make_xst_plots(
                block, station_name, timestamp, subband, rcu_mode,
                map_zoom=18, outputpath=temp_dir, mark_max_power=True,
                height=height, return_only_paths=True, caltable_dir=caltable_dir,
            )
            duration = time.time() - start_time
            print(f"Subband {subband} processed in {duration:.2f} seconds")
            # Log the generated near-field image to the system state
            if nf_img:
                filename = os.path.basename(nf_img)
                state.add_image_entry(filename, subband=subband)
        except Exception as e:
            print(f"Error processing subband {subband}: {e}")

    # Create a pool of worker threads
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        with open(filename, "rb") as f:
            while state.is_observing:
                # Read new data from the .dat stream
                new_data = np.fromfile(f, dtype=np.complex128)
                buffer = np.concatenate((buffer, new_data))

                # If enough data is accumulated to form a block, process it
                while buffer.size >= block_size:
                    block = buffer[:block_size].reshape((num_rcu, num_rcu))
                    buffer = buffer[block_size:]

                    block_counter += 1

                    # Increment subband_counter
                    subband = min_subband + (subband_counter % (max_subband - min_subband + 1))
                    subband_counter += 1

                    # Step filtering: only process 1 of every N blocks
                    if block_counter % step != 0:
                        continue

                    # Health checks: system is falling behind (currently inactive)
                    # if buffer.size > max_threads * block_size and block_counter > max_threads + 1:
                    #     pass  # Placeholder for future congestion control

                    # Timestamp for the processed block
                    obstime = datetime.datetime.now()

                    # Send block to be processed by an available thread
                    print(f"Submitting block {block_counter}, subband {subband}")
                    with pending_lock:
                        pending_tasks += 1
                    executor.submit(process_block_wrapper, block, subband, obstime)
                    with pending_lock:
                        print(f"Pending threads in executor: {pending_tasks}")


                # If no new data was read, wait before retrying
                if new_data.size == 0:
                    time.sleep(sleep_interval)

        print("Observation stopped from web interface.")




def obs_parser(obs_file):
    obs_data = {'beams': []}
    with open(obs_file) as obs:
        lines = obs.readlines()
        for line in lines:
            if line.startswith('bits='):
                obs_data['bits'] = line.split('=')[1].replace('\n', '')

            elif line.startswith('rspctl --bitmode'):
                obs_data['bits'] = line.split('=')[1].replace('\n', '')

            elif line.startswith('- rspctl --bitmode'):
                obs_data['bits'] = line.split('=')[1].replace('\n', '')

            elif line.startswith('subbands='):
                obs_data['subbands'] = line.split('=')[1].replace('\n', '').replace("'", "")

            elif line.startswith("nohup beamctl "):
                beam_data = line.split()
                obs_data['beams'].append({'name': beam_data[7].split("=")[1].replace('$', '').lstrip('0,0,'),
                                          'beamlets': beam_data[6].split("=")[1]})

            elif line.startswith("$PREFIX beamctl"):
                beam_data = line.split()
                obs_data['beams'].append({'name': beam_data[7].split("=")[1].replace('$', '').lstrip('0,0,'),
                                          'beamlets': beam_data[6].split("=")[1]})

            elif line.startswith("- beamctl "):
                line = line.replace("- ", "")
                beam_data = line.split()
                #source_name = get_source_name(beam_data[7].split("=")[1].replace('$', ''))
                #obs_data['beams'].append({'name': source_name, 'beamlets': beam_data[4].split("=")[1]})
    return obs_data


def get_subbands(input_path):
    # Find the observation file in the input path
    time.sleep(0.5)
    obs_files = [f for f in os.listdir(input_path) if f.endswith(('.h', '.sh'))]
    if obs_files:
        obs_file = os.path.join(input_path, obs_files[0])  # Use the first matching file
    else:
        raise FileNotFoundError("No observation file (.h, .sh) found in the input path.")

    obs_data = obs_parser(obs_file)

    if 'subbands' in obs_data:
        # Convert subbands string to a list of integers
        subbands = list(map(int, obs_data['subbands'].split(':')))
        min_subband = min(subbands)
        max_subband = max(subbands)
        print(f"Min subband: {min_subband}, Max subband: {max_subband}")
    else:
        # Allow manual input for subbands if not found in the observation file
        print("No subbands information found in the observation file. Please input manually.")
        min_subband = int(input("Enter the minimum subband: "))
        max_subband = int(input("Enter the maximum subband: "))
        if min_subband >= max_subband or min_subband < 0 or max_subband < 0:
            raise ValueError("No subbands information found in the observation file.")

    return min_subband, max_subband
