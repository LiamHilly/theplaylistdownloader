
from flask import Flask, request, send_file
import subprocess
import os
import uuid
import shutil

app = Flask(__name__)

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return {"error": "No URL provided"}, 400

    download_id = str(uuid.uuid4())
    output_folder = f"/tmp/{download_id}"
    os.makedirs(output_folder, exist_ok=True)

    try:
        # Download using yt-dlp
        subprocess.run([
            "yt-dlp", "--extract-audio", "--audio-format", "mp3", "-o",
            f"{output_folder}/%(title)s.%(ext)s", url
        ], check=True)

        # Zip the folder
        zip_path = f"/tmp/{download_id}.zip"
        shutil.make_archive(f"/tmp/{download_id}", 'zip', output_folder)
        return send_file(zip_path, as_attachment=True)

    except subprocess.CalledProcessError:
        return {"error": "Download failed"}, 500
    finally:
        shutil.rmtree(output_folder, ignore_errors=True)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
