
from flask import Flask, request, send_file
from flask_cors import CORS
import subprocess
import os
import uuid
import shutil

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data['url']
    
    # Use yt-dlp to download audio
    subprocess.run([
        'yt-dlp', '-x', '--audio-format', 'mp3',
        '-o', 'downloads/%(title)s.%(ext)s',
        url
    ])

    # Zip the folder
    shutil.make_archive('playlist', 'zip', 'downloads')

    # Send the zip file back to the frontend
    return send_file('playlist.zip', as_attachment=True)

    except subprocess.CalledProcessError:
        return {"error": "Download failed"}, 500
    finally:
        shutil.rmtree(output_folder, ignore_errors=True)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
