# webapp/app.py

from flask import Flask, render_template, request, redirect
import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from webapp import state, processor
from lofarimaging.rfi_tools.realtime import warmup_processing



app = Flask(__name__)

state.load_log()
#warmup_processing()


@app.route("/")
def index():
    sorted_log = state.image_log.copy()
    sorted_log["timestamp"] = pd.to_datetime(sorted_log["timestamp"], errors="coerce")
    last_images = (
        sorted_log
        .sort_values(by="timestamp", ascending=False)
        .head(5)
        .to_dict(orient="records")
    )
    return render_template("index.html", config=state.config, images=last_images, status=state.get_status())


@app.route("/start", methods=["POST"])
def start():
    if state.is_observing:
        print("Observation is already running. Ignoring new request.")
        return redirect("/")

    state.config["folder"] = request.form["folder"]
    state.config["threads"] = int(request.form["threads"])
    state.config["step"] = int(request.form["step"])
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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
