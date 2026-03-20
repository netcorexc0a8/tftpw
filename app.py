from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, abort
from pathlib import Path
import hashlib
import logging
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

__version__ = "1.2.5"

# Get the directory where this script is located
BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__, 
            template_folder=str(BASE_DIR / 'templates'),
            static_folder=str(BASE_DIR / 'static'))
app.secret_key = os.getenv('SECRET_KEY')

UPLOAD_FOLDER = Path("/dboot")
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 500)) * 1024 * 1024
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def get_file_hashes(path):
    try:
        data = path.read_bytes()
        return {
            "md5": hashlib.md5(data).hexdigest(),
            "sha256": hashlib.sha256(data).hexdigest(),
            "sha512": hashlib.sha512(data).hexdigest()
        }
    except Exception as e:
        logging.error(f"Error calculating hashes for {path}: {e}")
        return {"md5": "", "sha256": "", "sha512": ""}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        for file in request.files.getlist("file"):
            if file.filename and (secure_name := secure_filename(file.filename)):
                if file.content_length and file.content_length > MAX_CONTENT_LENGTH:
                    flash(f"File {file.filename} is too large (maximum {MAX_CONTENT_LENGTH // (1024*1024)} MB)")
                    continue
                try:
                    file.save(app.config["UPLOAD_FOLDER"] / secure_name)
                except Exception as e:
                    logging.error(f"Error saving file {file.filename}: {e}")
                    flash(f"Error saving file {file.filename}")
        return redirect(url_for("index"))

    try:
        files = sorted([f for f in app.config["UPLOAD_FOLDER"].iterdir() if f.is_file()], key=lambda x: str(x).lower())
        hashes = {f.name: get_file_hashes(f) for f in files}
    except Exception as e:
        logging.error(f"Error listing files: {e}")
        files, hashes = [], {}
    
    max_size_mb = MAX_CONTENT_LENGTH // (1024 * 1024)
    return render_template("index.html", files=[f.name for f in files], hashes=hashes, version=__version__, max_size_mb=max_size_mb)

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    if not (secure_name := secure_filename(filename)):
        abort(404)
    filepath = app.config["UPLOAD_FOLDER"] / secure_name
    if not filepath.exists() or not filepath.resolve().is_relative_to(app.config["UPLOAD_FOLDER"].resolve()):
        abort(404)
    return send_from_directory(app.config["UPLOAD_FOLDER"], secure_name, as_attachment=True)

@app.route("/delete/<filename>", methods=["GET"])
def delete_file(filename):
    if not (secure_name := secure_filename(filename)):
        return redirect(url_for("index"))
    path = app.config["UPLOAD_FOLDER"] / secure_name
    if path.resolve().is_relative_to(app.config["UPLOAD_FOLDER"].resolve()):
        try:
            path.unlink()
            logging.info(f"Deleted file: {path}")
        except Exception as e:
            logging.error(f"Error deleting {path}: {e}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
