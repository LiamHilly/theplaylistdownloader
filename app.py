
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
