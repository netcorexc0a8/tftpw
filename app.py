from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, flash
import os
import hashlib
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
logging.info("Flask app created")
app.secret_key = "supersecret"
UPLOAD_FOLDER = "/tftpboot"
logging.info(f"UPLOAD_FOLDER set to: {UPLOAD_FOLDER}")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
MAX_CONTENT_LENGTH = 500 * 1024 * 1024
logging.info(f"MAX_CONTENT_LENGTH set to: {MAX_CONTENT_LENGTH} bytes")
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>TFTP</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      background: #121212;
      color: #e0e0e0;
    }
    h1 { text-align: center; color: #ffffff; }
    .btn {
      background: #10a37f;
      color: white;
      padding: 8px 15px;
      text-decoration: none;
      border-radius: 5px;
      border: none;
      cursor: pointer;
      display: inline-block;
      font-size: inherit;
    }
    .btn.delete-btn { background: #e74c3c; }
    .btn:hover { opacity: 0.9; }
    #upload-form {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;
    }
    #file-upload { display: none; }
    #selected-files-list {
      margin-top: 10px;
      margin-bottom: 10px;
      font-size: 0.9em;
      color: #bbbbbb;
    }
    .file-card {
      border: 1px solid #333;
      border-radius: 10px;
      padding: 15px;
      margin-bottom: 15px;
      background: #1e1e1e;
      box-shadow: 0 2px 4px rgba(0,0,0,0.5);
      max-width: 100%;
      overflow: hidden;
      word-wrap: break-word;
    }
    .file-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    .file-name {
      font-weight: bold;
      word-break: break-word;
      flex: 1;
    }
    .file-actions {
      display: flex;
      gap: 10px;
      flex-shrink: 0;
    }
    .file-actions a {
      text-decoration: none;
      color: white;
    }
    .file-actions a:hover {
      text-decoration: none;
    }
    .file-hash {
      font-size: 0.85em;
      color: #aaaaaa;
      word-break: break-all;
      overflow-wrap: break-word;
      margin-top: 5px;
      max-width: 100%;
    }
    .file-hash div {
      display: block;
      margin-bottom: 2px;
    }
    .progress-container {
      margin-top: 10px;
      margin-bottom: 10px;
      display: none;
      background: #333;
      border-radius: 4px;
    }
    .file-progress-bar {
      position: relative;
      height: 12px;
    }
    .file-progress-text {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      text-align: center;
      color: white;
      font-size: 12px;
      line-height: 12px;
    }
    .progress-bar {
      height: 16px;
      background: #10a37f;
      width: 0%;
      border-radius: 4px;
      transition: width 0.3s;
      position: relative;
    }
    #progress-text {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      text-align: center;
      color: white;
      font-size: 16px;
      font-weight: bold;
      line-height: 16px;
    }
    .flash {
      color: #ff5555;
      text-align: center;
      margin-bottom: 15px;
    }
  </style>
</head>
<body>
  <h1>📂 Files on TFTP Server</h1>

  {% with messages = get_flashed_messages() %}
    {% if messages %}
      <div class="flash">{{ messages[0] }}</div>
    {% endif %}
  {% endwith %}

  <form id="upload-form" method="post" enctype="multipart/form-data">
    <label for="file-upload" class="btn">📂 Select File</label>
    <input id="file-upload" type="file" name="file" multiple>
    <button type="submit" class="btn">⬆️ Upload</button>
  </form>

  <div id="selected-files-list"></div>

  <div class="progress-container" id="progress-container">
    <div class="progress-bar" id="progress-bar"><span id="progress-text"></span></div>
  </div>

  {% for file in files %}
  <div class="file-card">
    <div class="file-header">
      <span class="file-name">{{ file }}</span>
      <div class="file-actions">
        <a href="{{ url_for('download_file', filename=file) }}" class="btn">⬇️ Download</a>
        <a href="{{ url_for('delete_file', filename=file) }}" class="btn delete-btn">🗑️ Delete</a>
      </div>
    </div>
    <div class="file-hash">
      <div><strong>MD5:</strong> {{ hashes[file]['md5'] }}</div>
      <div><strong>SHA-512:</strong> {{ hashes[file]['sha512'] }}</div>
    </div>
  </div>
  {% endfor %}

  <script>
    const form = document.getElementById("upload-form");
    const fileInput = document.getElementById("file-upload");
    const selectedFilesList = document.getElementById("selected-files-list");
    const progressContainer = document.getElementById("progress-container");
    const progressBar = document.getElementById("progress-bar");
    const progressText = document.getElementById("progress-text");

    // Display selected files with sizes in KB or MB and individual progress bars
    fileInput.addEventListener("change", () => {
      selectedFilesList.innerHTML = "";
      Array.from(fileInput.files).forEach(file => {
        let sizeText;
        if (file.size < 1024 * 1024) {
          const sizeKB = Math.round(file.size / 1024);
          sizeText = `${sizeKB} KB`;
        } else {
          const sizeMB = Math.round(file.size / (1024 * 1024));
          sizeText = `${sizeMB} MB`;
        }
        const div = document.createElement("div");
        div.style.display = "flex";
        div.style.justifyContent = "flex-start";
        div.style.alignItems = "center";
        div.style.gap = "10px";
        div.innerHTML = `
          <div>📄 ${file.name} (${sizeText})</div>
          <div class="file-progress-container" style="display: none; width: 200px;">
            <div class="file-progress-bar" style="height: 12px; background: #10a37f; width: 0%; border-radius: 4px;">
              <div class="file-progress-text">0%</div>
            </div>
          </div>
        `;
        selectedFilesList.appendChild(div);
      });
    });

    // Upload selected files one by one with individual progress
    form.addEventListener("submit", function(e) {
      e.preventDefault();
      if (fileInput.files.length === 0) return;

      const files = Array.from(fileInput.files);
      let completed = 0;

      files.forEach((file, index) => {
        const formData = new FormData();
        formData.append("file", file);

        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/", true);

        const fileDiv = selectedFilesList.children[index];
        const progressContainer = fileDiv.querySelector('.file-progress-container');
        const progressBar = progressContainer.querySelector('.file-progress-bar');
        const progressText = progressContainer.querySelector('.file-progress-text');

        progressContainer.style.display = "block";

        xhr.upload.onprogress = function(e) {
          if (e.lengthComputable) {
            const percent = (e.loaded / e.total) * 100;
            progressBar.style.width = percent + "%";
            progressText.textContent = Math.round(percent) + "%";
          }
        };

        xhr.onload = function() {
          if (xhr.status === 200) {
            progressBar.style.width = "100%";
            progressText.textContent = "Calculating hashes...";
            completed++;
            if (completed === files.length) {
              setTimeout(() => location.reload(), 2000);
            }
          } else {
            alert("Error uploading " + file.name);
          }
        };

        xhr.send(formData);
      });
    });

    // Debug: Log font sizes of buttons
    console.log('Label button font-size:', window.getComputedStyle(document.querySelector('label.btn')).fontSize);
    console.log('Submit button font-size:', window.getComputedStyle(document.querySelector('button.btn')).fontSize);
    document.querySelectorAll('a.btn').forEach((btn, index) => {
      console.log(`A button ${index} font-size:`, window.getComputedStyle(btn).fontSize);
    });
  </script>
</body>
</html>
"""

def get_file_hashes(path):
    logging.debug(f"Calculating hashes for file: {path}")
    hashes = {"md5": "", "sha512": ""}
    try:
        with open(path, "rb") as f:
            data = f.read()
            hashes["md5"] = hashlib.md5(data).hexdigest()
            hashes["sha512"] = hashlib.sha512(data).hexdigest()
        logging.debug(f"Hashes calculated for {path}: MD5={hashes['md5'][:8]}..., SHA512={hashes['sha512'][:8]}...")
    except Exception as e:
        logging.error(f"Error calculating hashes for {path}: {e}")
    return hashes

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        files = request.files.getlist("file")
        logging.info(f"Received upload request for files: {[f.filename for f in files if f.filename]}")
        for file in files:
            if file.filename:
                logging.debug(f"Processing file: {file.filename}, size: {file.content_length}")
                if file.content_length and file.content_length > MAX_CONTENT_LENGTH:
                    logging.warning(f"File {file.filename} too large: {file.content_length} > {MAX_CONTENT_LENGTH} (max message says 200 MB)")
                    flash(f"File {file.filename} is too large (maximum 500 MB)")
                    continue
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                logging.info(f"Saving file to: {filepath}")
                file.save(filepath)
        return redirect(url_for("index"))

    try:
        files = sorted(os.listdir(app.config["UPLOAD_FOLDER"]), key=lambda x: x.lower())
        logging.info(f"Listing files in {app.config['UPLOAD_FOLDER']}: {files}")
        hashes = {}
        for f in files:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], f)
            if os.path.exists(filepath):
                hashes[f] = get_file_hashes(filepath)
            else:
                logging.warning(f"File {filepath} does not exist during hashing")
    except Exception as e:
        logging.error(f"Error listing files: {e}")
        files = []
        hashes = {}
    return render_template_string(TEMPLATE, files=files, hashes=hashes)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

@app.route("/delete/<filename>")
def delete_file(filename):
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    logging.info(f"Attempting to delete file: {path}")
    if os.path.exists(path):
        try:
            os.remove(path)
            logging.info(f"Deleted file: {path}")
        except Exception as e:
            logging.error(f"Error deleting {path}: {e}")
    else:
        logging.warning(f"File not found for deletion: {path}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
