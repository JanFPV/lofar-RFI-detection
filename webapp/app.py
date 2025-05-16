# webapp/app.py

from flask import Flask, render_template, request, redirect
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from webapp import state, processor


app = Flask(__name__)


state.load_log()


@app.route("/")
def index():
    # Últimas 5 imágenes
    last_images = state.image_log.tail(5).to_dict(orient="records")
    return render_template("index.html", config=state.config, images=last_images)

@app.route("/start", methods=["POST"])
def start():
    state.config["folder"] = request.form["folder"]
    state.config["threads"] = int(request.form["threads"])
    state.config["step"] = int(request.form["step"])
    state.is_observing = True

    processor.start_observation()

    return redirect("/")


@app.route("/stop", methods=["POST"])
def stop():
    state.is_observing = False
    state.save_log()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
