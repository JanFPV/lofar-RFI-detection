import os
import glob
import datetime
import re
import pandas as pd

__all__ = [
    "get_subbands",
    "get_obstime",
    "analyze_files",
    "print_summary",
]


def get_subbands(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    match = re.search(r'--xcsubband=(\d+)', content)
    return int(match.group(1)) if match else None


def get_obstime(file_path):
    obsdatestr, obstimestr, *_ = os.path.basename(file_path).rstrip(".dat").split("_")
    return datetime.datetime.strptime(obsdatestr + ":" + obstimestr, '%Y%m%d:%H%M%S')


def analyze_files(data_files):
    dat_files = sorted(glob.glob(os.path.join(data_files, '*.dat')))
    h_files = sorted(glob.glob(os.path.join(data_files, '*.h')))

    assert len(dat_files) == len(h_files), "Mismatch in number of .dat and .h files"

    data_list = []

    for dat_file, h_file in zip(dat_files, h_files):
        timestamp = get_obstime(dat_file)
        timestamp2 = get_obstime(h_file)
        if timestamp != timestamp2:
            print(f"Warning: timestamps do not match for {dat_file} and {h_file}")
        subband = get_subbands(h_file)

        data_list.append({
            "timestamp": timestamp,
            "subband": subband,
            "dat_file": dat_file,
            "h_file": h_file
        })

    df = pd.DataFrame(data_list)
    df = df.sort_values(by=["timestamp", "subband"]).reset_index(drop=True)

    average_measures_per_subband = round(df["subband"].value_counts().mean(), 2)
    measurement_duration = round((df["timestamp"].max() - df["timestamp"].min()).total_seconds() / len(df), 2) if len(df) > 1 else None

    summary = {
        "number_of_files": len(df),
        "subbands_available": {
            "first_subband": df["subband"].min(),
            "last_subband": df["subband"].max(),
            "total_subbands": len(df["subband"].dropna().unique())
        },
        "start_time": df["timestamp"].min(),
        "end_time": df["timestamp"].max(),
        "average_measures_per_subband": average_measures_per_subband,
        "measurement_duration": measurement_duration
    }

    return df, summary


def print_summary(summary):
    print("Summary of Analyzed Files:")
    print(f"Number of files: {summary['number_of_files']}")
    print(f"First and last subband: {summary['subbands_available']['first_subband']} - {summary['subbands_available']['last_subband']}")
    print(f"Total subbands: {summary['subbands_available']['total_subbands']}")
    print(f"Start time: {summary['start_time']}")
    print(f"End time: {summary['end_time']}")
    print(f"Average measurements per subband: {summary['average_measures_per_subband']}")
    print(f"Average measurement duration: {summary['measurement_duration']} seconds")
