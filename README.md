# LOFAR Single Station Imaging for RFI Detection

This repository is part of my Bachelor's thesis project at VUAS, which aims to use LOFAR in standalone mode to detect and measure radio frequency interference (RFI) at the LOFAR station in Irbene.

## Installation
To install and set up the environment, follow these steps:

```sh
# Clone the repository
git clone https://github.com/JanFPV/lofar-RFI-detection.git
cd lofar-RFI-detection

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'

# Install dependencies
pip install -r requirements.txt
```

## Calibration Tables
This repository includes calibration tables specifically for the Irbene LOFAR station, so no additional downloads are required.

## Running the Notebook
Open the notebook in a Jupyter Notebook, JupyterLab, or VS Code instance:

```sh
jupyter notebook
```

In VS Code, open the notebook file and ensure the Python extension is installed to run the cells interactively.

To run all cells in the notebook:

```
Kernel > Restart & Run All
```

---

This project extends LOFAR single-station imaging capabilities to enable standalone RFI detection and analysis, focusing on data collected at the Irbene LOFAR station.

