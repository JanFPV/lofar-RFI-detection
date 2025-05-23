# LOFAR RFI Detection System

This repository enables real-time radio frequency interference (RFI) detection using a single LOFAR station in Irbene (LV614). It was developed as part of a Bachelor's thesis at Ventspils University of Applied Sciences (VUAS).

The core functionality combines adapted modules from the official [lofarimaging](https://github.com/lofar-astron/lofarimaging) repository with newly developed tools for real-time visualization and user interaction. The system is written in Python 3.12 and can optionally be run using Docker with Docker Compose v2.

---

## Project Overview

The code under `lofarimaging/` comes from the upstream `lofarimaging` repository, but has been **extensively modified** to:

- Add new functionalities for near-field imaging
- Improve integration with real-time workflows
- Support user-defined configuration during observation

The subfolder `lofarimaging/rfi_tools/` contains all **original modules written for this thesis**, which:

- Wrap and extend functionality from the LOFAR imaging core
- Provide tools to generate image sweeps
- Enable real-time processing (including multithreaded handling of image generation)

The `webapp/` directory contains both the backend and frontend code for a basic web interface that allows users to launch and monitor real-time observations, configure parameters, view live-generated images, and access logs. This interface integrates the tools in `rfi_tools` with Flask and a minimal HTML+JS frontend.

---

## Calibration Tables

This repository includes calibration tables specifically for the Irbene LOFAR station, so no additional downloads are required.

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

#### Production Mode (Prebuilt image from GHCR)

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

### A. Clone and set up manually

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

### B. Launch via Docker

```bash
# Run in production mode (prebuilt image)
docker compose up

# Run in development mode (build from source code)
docker compose -f docker-compose.local.yml up --build
```

### C. Generate test data (optional)

```bash
python scripts/data_generator.py
```

---

## System Requirements

- Python 3.12 (for manual runs)
- Docker + Docker Compose v2
- Stable disk I/O (for writing .dat blocks)
- No specific CPU performance requirements: the system allows adjusting the number of threads and the processing step to accommodate slower or faster machines

---

## Known Bugs and Limitations

- `server.log` can grow large, affecting log viewer
- Notebooks may use outdated structure
- If an observation is started and no `.dat` file appears, pressing "Stop" will not terminate the process and a Docker restart may be required
- If a non-existent folder is entered as input, the processing thread will crash

---

## Features Pending / Future Work

- Create sweep video from web
- Develop Web interface for postprocessing
- UI polish for responsiveness

---

This repository supports modular, standalone RFI detection using LOFAR data. It bridges scientific imaging, real-time automation, and interactive visualization in a single framework. 

---

This project extends LOFAR single-station imaging capabilities to enable standalone RFI detection and analysis, focusing on data collected at the Irbene LOFAR station.

Feel free to explore, modify, or extend the system to match your research or operational needs.

This project is distributed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for more details.
