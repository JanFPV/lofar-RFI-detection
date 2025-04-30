# LOFAR Single Station Imaging for RFI Detection

This repository is part of my Bachelor's thesis project at VUAS, which aims to use LOFAR in standalone mode to detect and measure radio frequency interference (RFI) at the LOFAR station in Irbene.

Tested and run in Python 3.12

## Installation
To install and set up the environment, follow these steps:

```sh
# Clone the repository
git clone https://github.com/JanFPV/lofar-RFI-detection.git
cd lofar-RFI-detection

# Create and activate a virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'

# Install dependencies
pip3.12 install -r requirements.txt
```

## Calibration Tables
This repository includes calibration tables specifically for the Irbene LOFAR station, so no additional downloads are required.

## Running Real Time observation
To run a real observation, clone the repository and create an environment, then, start an observation and give the path as an argument to the following script:
```sh
python3.12 scripts/realtime_movie_generation.py path-to-dat-file
```

## Running the Notebook
Open the notebook in a Jupyter Notebook, JupyterLab, or VS Code instance:

```sh
jupyter notebook
```
or
```sh
code .
```

In VS Code, open the notebook file and ensure the Python extension is installed to run the cells interactively.

To run all cells in the notebook:

```
Kernel > Restart & Run All
```

## Using Docker (Optional)

You can run the project in a self-contained Docker environment instead of installing Python and dependencies manually.

### 1. Install docker and compose

- Docker: https://docs.docker.com/get-docker/
- Docker Compose: https://docs.docker.com/compose/

### 2. Run the script using Docker Compose

If you have a directory (e.g., `/home/user/Desktop/test`) containing the real-time observation file, you can mount it into the container and pass it as an argument:

```sh
docker-compose run --rm \
  -v /home/user/Desktop/test:/data \
  lofar
```
> Note: This command will take a few minutes the first time it is run.

This will run the script as:
```sh
python scripts/realtime_movie_generation.py /data
```

Inside the container, `/data` points to your local `/data/de/prueba`.

> Note: This assumes your script reads a file from the directory and writes results back into the same path.

### 3. Notes

Docker support is optional and does not replace the ability to run the project via virtual environments or notebooks.

---

This project extends LOFAR single-station imaging capabilities to enable standalone RFI detection and analysis, focusing on data collected at the Irbene LOFAR station.

