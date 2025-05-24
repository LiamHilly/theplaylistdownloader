
from flask import Flask, request, send_file
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

    # Clean up previous downloads
    if os.path.exists(DOWNLOADS_DIR):
        shutil.rmtree(DOWNLOADS_DIR)
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

    try:
        # Use yt-dlp to download audio
        subprocess.run([
            'yt-dlp', '-x', '--audio-format', 'mp3',
            '-o', f'{DOWNLOADS_DIR}/%(title)s.%(ext)s',
            url
        ], check=True)

        # Zip the folder
        shutil.make_archive('playlist', 'zip', DOWNLOADS_DIR)

        print("[INFO] Creating zip archive...")
shutil.make_archive('playlist', 'zip', DOWNLOADS_DIR)

if not os.path.exists('playlist.zip'):
    print("[ERROR] playlist.zip not found.")
    return jsonify({"error": "Zip file was not created"}), 500

size = os.path.getsize('playlist.zip')
print(f"[INFO] Sending zip file, size: {size} bytes")
return send_file('playlist.zip', as_attachment=True)

        # Send the zip file back to the frontend
        return send_file('playlist.zip', as_attachment=True)

    except subprocess.CalledProcessError:
        return {"error": "Failed to download playlist"}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
