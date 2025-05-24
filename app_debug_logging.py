
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import shutil
import os

app = Flask(__name__)
CORS(app)

DOWNLOADS_DIR = "downloads"

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data['url']
    print(f"[INFO] Received URL: {url}")

    # Clean up previous downloads
    if os.path.exists(DOWNLOADS_DIR):
        print("[INFO] Cleaning up previous downloads.")
        shutil.rmtree(DOWNLOADS_DIR)
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

    try:
        print("[INFO] Starting yt-dlp download...")
        subprocess.run([
            'yt-dlp', '-x', '--audio-format', 'mp3',
            '-o', f'{DOWNLOADS_DIR}/%(title)s.%(ext)s',
            url
        ], check=True)
        print("[INFO] Download complete.")

        print("[INFO] Creating zip archive...")
        shutil.make_archive('playlist', 'zip', DOWNLOADS_DIR)

        if not os.path.exists('playlist.zip'):
            print("[ERROR] playlist.zip not found.")
            return jsonify({"error": "Zip file was not created"}), 500

        size = os.path.getsize('playlist.zip')
        print(f"[INFO] Sending zip file, size: {size} bytes")

        return send_file('playlist.zip', as_attachment=True)

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Download failed: {e}")
        return jsonify({"error": "Failed to download playlist"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
