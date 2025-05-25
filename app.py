
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import shutil
import os
import threading
import signal

app = Flask(__name__)
CORS(app)

DOWNLOADS_DIR = "downloads"
STATUS_FILE = "status.txt"
TRACKS_FILE = "tracks.txt"
yt_dlp_process = None

def write_status(msg):
    with open(STATUS_FILE, 'w') as f:
        f.write(msg)

def append_track(track_name):
    with open(TRACKS_FILE, 'a') as f:
        f.write(track_name + "\n")

def clear_tracking_files():
    for file in [STATUS_FILE, TRACKS_FILE]:
        if os.path.exists(file):
            os.remove(file)

@app.route('/status', methods=['GET'])
def status():
    status = "Idle"
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            status = f.read()
    tracks = []
    if os.path.exists(TRACKS_FILE):
        with open(TRACKS_FILE, 'r') as f:
            tracks = f.read().splitlines()
    return jsonify({"status": status, "tracks": tracks})

@app.route('/cancel', methods=['POST'])
def cancel():
    global yt_dlp_process
    if yt_dlp_process and yt_dlp_process.poll() is None:
        yt_dlp_process.send_signal(signal.SIGINT)
        write_status("Download cancelled.")
        return jsonify({"message": "Cancelled"})
    else:
        return jsonify({"message": "No active process"}), 400

@app.route('/download', methods=['POST'])
def download():
    global yt_dlp_process

    def run_download(url):
        try:
            clear_tracking_files()
            write_status("[1/4] Cleaning previous downloads...")
            if os.path.exists(DOWNLOADS_DIR):
                shutil.rmtree(DOWNLOADS_DIR)
            os.makedirs(DOWNLOADS_DIR, exist_ok=True)

            write_status("[2/4] Downloading tracks...")

            yt_dlp_process = subprocess.Popen([
                'yt-dlp',
                '-x', '--audio-format', 'mp3',
                '-o', f'{DOWNLOADS_DIR}/%(title)s.%(ext)s',
                '--print', '%(title)s',
                '--progress-template', 'default',
                '--newline',
                url
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            for line in yt_dlp_process.stdout:
                print(line.strip())
                if line.startswith('[ExtractAudio] Destination:'):
                    filename = line.strip().split('Destination:')[-1].strip()
                    track_title = os.path.basename(filename)
                    append_track(track_title)
                elif 'Deleting original file' in line:
                    downloaded = len(open(TRACKS_FILE).readlines())
                    write_status(f"[2/4] Downloading tracks... ({downloaded})")

            yt_dlp_process.wait()

            if yt_dlp_process.returncode == 0:
                write_status("[3/4] Zipping files...")
                shutil.make_archive('playlist', 'zip', DOWNLOADS_DIR)
                write_status("[4/4] Download ready.")
            else:
                write_status("[ERROR] Download was interrupted or failed.")

        except Exception as e:
            write_status(f"[ERROR] {str(e)}")

    data = request.get_json()
    url = data['url']
    write_status("Starting download...")

    thread = threading.Thread(target=run_download, args=(url,))
    thread.start()

    return jsonify({"message": "Download started"})

@app.route('/download-file', methods=['GET'])
def download_file():
    if os.path.exists("playlist.zip"):
        return send_file("playlist.zip", as_attachment=True)
    return jsonify({"error": "No file found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
