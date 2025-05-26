from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import os
import shutil

app = Flask(__name__)
CORS(app)

DOWNLOADS_DIR = "downloads"

@app.route("/download", methods=["POST"])
def download_playlist():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"success": False, "message": "URL missing"}), 400

    if os.path.exists(DOWNLOADS_DIR):
        shutil.rmtree(DOWNLOADS_DIR)
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

    try:
        subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3", url, "-P", DOWNLOADS_DIR],
            check=True
        )
        shutil.make_archive("playlist", "zip", DOWNLOADS_DIR)
        return jsonify({"success": True})
    except subprocess.CalledProcessError:
        return jsonify({"success": False, "message": "Download failed"}), 500

@app.route("/download-file", methods=["GET"])
def download_file():
    return send_file("playlist.zip", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)