# LOFAR RFI Detection System

This repository enables real-time radio frequency interference (RFI) detection using a single LOFAR station in Irbene (LV614). It was developed as part of a Bachelor's thesis at Ventspils University of Applied Sciences (VUAS).

The core functionality combines adapted modules from the official [lofarimaging](https://github.com/lofar-astron/lofarimaging) repository with newly developed tools for real-time visualization and user interaction. The system is written in Python 3.12 and can optionally be run using Docker with Docker Compose v2.

---

## Project Overview

The code under `lofarimaging/` comes from the upstream `lofarimaging` repository, but has been **extensively modified** to:

- Add new functionalities for near-field imaging, such as source tracking
- Improve integration with real-time workflows
- Support user-defined configuration during observation

The subfolder `lofarimaging/rfi_tools/` contains all **original modules written for this thesis**, which:

- Wrap and extend functionality from the LOFAR imaging core
- Provide tools to generate image sweeps
- Enable real-time processing (including multithreaded handling of image generation)

The `webapp/` directory contains both the backend and frontend code for a basic web interface that allows users to launch and monitor real-time observations, configure parameters, view live-generated images, and access logs. This interface integrates the tools in `rfi_tools` with Flask and a minimal HTML+JS frontend.

---

## Modes of Use

### 1. Jupyter Notebooks (Exploratory/Development)

Located in the `notebooks/` folder, these allow interactive exploration and visualization using modules from both `lofarimaging` and `rfi_tools`.

**Setup:**

```bash
# Create a new Python virtual environment
python3.12 -m venv venv

# Activate the environment (Linux)
source venv/bin/activate

# Install project dependencies
pip install -r requirements.txt

# Launch Jupyter Notebooks
jupyter notebook

# or open the folder directly in VS Code
code .
```

Or use:

```bash
./envsetup.sh
```

### 2. Script Execution (Terminal-based)

- `scripts/realtime_movie_generation.py` – legacy real-time processor
- `scripts/data_generator.py` – fake `.dat` file generator for testing

These are functional but mostly superseded by the Docker interface.

### 3. Docker (Recommended)

Launches a **web interface** with real-time processing and image viewing. Two modes:

#### Regular User (Prebuilt image from GHCR)

```bash
docker compose up
```

#### 2. Local Development (Build from source)

```bash
docker compose -f docker-compose.local.yml up --build
```

Access the interface at:

```
http://localhost:5000
```

---

## Instructions

### 1. Clone and set up manually

```bash
git clone https://github.com/JanFPV/lofar-RFI-detection.git
cd lofar-RFI-detection
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Or run:

```bash
./envsetup.sh
```

### 2. Launch via Docker

```bash
# Run in production mode (prebuilt image)
docker compose up

# Run in development mode (build from source code)
docker compose -f docker-compose.local.yml up --build
```

### 3. Generate fake observation data (optional)

```bash
python scripts/data_generator.py
```

---

## Calibration Tables

This repository includes calibration tables specifically for the Irbene LOFAR station, so no additional downloads are required.

---

## System Requirements

- Python 3.12 (for manual runs)
- Docker + Docker Compose v2 (for web interface)
- Stable disk I/O (for writing .dat blocks)
- No specific CPU performance requirements: the system allows adjusting the number of threads and the block discarding step to accommodate slower or faster machines

---

## Known Bugs and Limitations

- **Image Scale Normalization:** The intensity scale currently adjusts dynamically for each individual image. This can cause minor, insignificant interference to appear magnified when no strong signal is present. A manual override for the intensity scale or a global normalization system that applies a consistent scale across multiple images should be implemented.
- **Incorrect Timestamping in Real-Time Observations:** During live data capture, data blocks are sometimes received in bursts rather than steadily at one per second. The current system assigns a timestamp upon arrival, which causes multiple blocks to receive the same timestamp, leading to data being overwritten and lost. This should be fixed by assigning timestamps sequentially (e.g., `previous_timestamp + 1s`) to ensure data integrity.
- **Excessive Log Growth:** The `server.log` file can grow indefinitely, which can impact the performance of the log viewer. Log rotation should be implemented.
- **Process Termination Failure:** If an observation is started but no `.dat` file is generated, the "Stop" button may fail to terminate the process, potentially requiring a manual restart of the Docker container.
- **Crash on Invalid Directory:** Providing a path to a non-existent directory as input can cause the processing thread to crash, requiring a Docker restart to recover.
- **Outdated Notebooks:** Some of the included Jupyter notebooks may be based on an older project structure and might require modifications to function correctly with the current version.

---

## Features Pending / Future Work

- Create sweep videos from web interface (modules are ready, but integration is pending)
- Develop Web interface for data postprocessing
- UI polish for responsiveness
- Implement database integration for better data management
- Add user login to secure access and personalize experience

---

This repository supports modular, standalone RFI detection using LOFAR data. It bridges scientific imaging, real-time automation, and interactive visualization in a single framework. It allows RFI detection and analysis, focusing on data collected at the Irbene LOFAR station.

Feel free to explore, modify, or extend the system to match your research or operational needs.

This project is distributed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for more details.
