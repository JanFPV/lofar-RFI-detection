# webapp/app.py

from flask import Flask, render_template, request, redirect, jsonify, abort
import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from webapp import state, processor
from lofarimaging.rfi_tools.realtime import warmup_processing



app = Flask(__name__)

state.past_observations = state.load_all_logs_by_observation()
#warmup_processing()


@app.route("/")
def index():
    sorted_log = state.image_log.copy()
    sorted_log["timestamp"] = pd.to_datetime(sorted_log["timestamp"], errors="coerce")
    last_images = (
        sorted_log
        .sort_values(by="timestamp", ascending=False)
        .head(20)
        .to_dict(orient="records")
    )
    past_observations = sorted(os.listdir(config.IMAGES_FOLDER), reverse=True)
    return render_template("index.html", config=state.config, images=last_images, past_observations=past_observations, status=state.get_status())


@app.route("/start", methods=["POST"])
def start():
    if state.is_observing:
        print("Observation is already running. Ignoring new request.")
        return redirect("/")

    state.config["folder"] = request.form["folder"]
    state.config["threads"] = int(request.form["threads"])
    state.config["step"] = int(request.form["step"])
    state.config["height_m"] = float(request.form["height_m"])
    state.config["extent"] = float(request.form["extent"])

    state.is_observing = True
    state.shutdown_requested = False
    state.system_status = "Running"

    processor.start_observation()
    return redirect("/")


@app.route("/stop", methods=["POST"])
def stop():
    state.shutdown_requested = True
    state.is_observing = False
    state.system_status = "Stopping..."
    print("Stop requested via web interface.")
    return redirect("/")


@app.route("/last-images")
def last_images():
    if not state.observation_path:
        return jsonify([])

    obs_name = os.path.basename(state.observation_path)

    if state.is_observing:
        log = state.image_log.copy()
        # print(f"[LIVE] Returning in-memory log: {len(log)} entries")
    else:
        log = state.past_observations.get(obs_name)
        # print(f"[LOG FILE] Returning saved log for {obs_name}: {len(log) if log is not None else 0} entries")

    if log is None or log.empty:
        return jsonify([])

    log["timestamp"] = pd.to_datetime(log["timestamp"], errors="coerce")
    latest = log.sort_values(by="timestamp", ascending=False).head(20)
    return jsonify(latest.to_dict(orient="records"))


@app.route("/system-status")
def system_status():
    return jsonify(state.get_status())


@app.route("/observation/<obs_name>/")
def browse_observation(obs_name):
    folder_path = os.path.join("webapp/static/images", obs_name)
    if not os.path.exists(folder_path):
        abort(404)

    file_list = []
    for root, _, files in os.walk(folder_path):
        rel_root = os.path.relpath(root, folder_path)
        for f in files:
            rel_path = os.path.join(rel_root, f) if rel_root != '.' else f
            file_list.append(rel_path)

    return render_template("browse.html", obs_name=obs_name, files=sorted(file_list))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
