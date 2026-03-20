# TFTPW v1.2.5

A web interface for managing a TFTPW server, built with Python Flask. Allows uploading, downloading, and deleting files with file hash display (MD5, SHA-256, and SHA-512) and upload progress bars.

---

## Project Structure

```
tftpw/
├── app.py             # Flask application main file
├── templates/         # Jinja2 HTML templates
│   └── index.html     # Main web interface template
├── static/            # Static files (CSS, JS, images)
│   └── js/
│       └── main.js    # JavaScript for web interface
├── data/              # Directory for TFTP files (mounted volume)
├── Dockerfile         # Docker image configuration
├── docker-compose.yml # Docker Compose configuration
└── README.md          # This file
```

---

## Features

- **Multiple file uploads** simultaneously.
- **File preview** with sizes displayed in KB or MB before upload.
- **File cards** with MD5, SHA-256, and SHA-512 hashes.
- **Click to copy** filename or hash to clipboard with toast notification.
- **Individual progress bars** for each file during upload.
- **Download and Delete buttons** for each file.
- **Upload progress bar**.
- **Dark theme** interface.
- **File sorting** by name (case-insensitive).
- **File size validation** before upload.
- Maximum upload file size: configurable via `MAX_CONTENT_LENGTH` (default 500 MB).
- Full Docker compatibility.

---

## Requirements

- Docker and Docker Compose installed on your system.
- Ports 5000 (HTTP) and 69/UDP (TFTP) available.
- GitLab CI/CD configured with required variables (for automated deployment).

---

## Environment Variables

The application uses environment variables for configuration. Create a `.env` file in the project root with the following variables:

- `SECRET_KEY`: A secret key used by Flask for session management and security. This should be a long, random string.
- `MAX_CONTENT_LENGTH`: Maximum file size for uploads in MB (default: 500MB).

Example `.env` file:

```
SECRET_KEY=your_secret_key_here
MAX_CONTENT_LENGTH=500
```

**Note:** The `.env` file is ignored by Git for security reasons. Never commit sensitive information.

---

## Installation and Running

The project is designed to run entirely in Docker. Follow these steps:

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd <project-directory>
    ```

2. Ensure the `data` directory exists for TFTP files:
    ```bash
    mkdir -p data
    ```

3. Configure environment variables:
    Copy the example `.env` file and set your values:
    ```bash
    cp .env .env.local  # or edit .env directly
    ```
    Edit the `.env` file to set the required variables (see Environment Variables section above).

4. Build and start the services using Docker Compose:
    ```bash
    docker compose build
    docker compose up -d
    ```

5. Access the web interface at `http://localhost:5000`.

The TFTPW server will be running on port 69/UDP, and files will be stored in the `./data` directory on the host.

---

## Usage

- Click **📂 Select File** to choose one or more files.
- File sizes will be displayed in KB or MB below the button.
- Click **⬆️ Upload** to send the files to the server.
- Each file shows an individual progress bar during upload.
- Uploaded files are listed as cards with:
  - File name (click to copy to clipboard)
  - **⬇️ Download** and **🗑️ Delete** buttons
  - MD5, SHA-256, and SHA-512 hashes (click any hash to copy)
- A toast notification appears when text is copied to clipboard.
- Cards are automatically sorted by file name.
- Changes (uploads, deletions) refresh the page automatically.

---

## Troubleshooting

### Common Issues

1. **Port conflicts**:
    - Ensure ports 5000 and 69 are not in use by other services.
    - Check with: `netstat -an | grep :5000` or `netstat -an | grep :69`.
    - Solution: Stop conflicting services or change ports in `docker-compose.yml` and `Dockerfile`.

2. **Docker build fails**:
    - Ensure Docker is installed and running.
    - Check disk space and internet connection for downloading images.
    - Solution: Run `docker system prune` to clean up, then retry.

3. **Files not uploading**:
     - Check file size: Maximum size is set by `MAX_CONTENT_LENGTH` (default 500 MB).
     - Verify `./data` directory permissions: `chmod 755 data`.
     - Check container logs: `docker compose logs tftp`.

4. **Hashes not displaying**:
    - Ensure files are properly saved in `./data`.
    - Check app logs inside container for errors.

5. **Cannot access web interface**:
    - Confirm the container is running: `docker compose ps`.
    - Try `http://127.0.0.1:5000` or your machine's IP.
    - Firewall may block port 5000.

6. **TFTPW server not responding**:
    - Verify atftpd is running in the container.
    - Check UDP port 69: `docker compose exec tftp netstat -uln | grep :69`.

7. **Permission issues on Windows**:
    - Ensure Docker Desktop has access to the project directory.
    - Run commands in an elevated terminal if needed.

If issues persist, check full logs: `docker compose logs` and search for error messages.

---

## Notes

- Maximum file size: configurable via `MAX_CONTENT_LENGTH` (default 500 MB).
- Interface is fully dark-themed for comfortable nighttime use.
- All operations (upload, delete) trigger automatic page refreshes.
- Individual progress bars show upload status for each file in real-time.
- Supports concurrent file uploads from multiple users.
- TFTPW server runs as a daemon inside the Docker container alongside the Flask app.
- Click on filename or any hash to copy to clipboard with toast notification.
- File sizes are displayed in KB for files under 1 MB, and in MB for larger files.
- SHA-256 hash is now displayed alongside MD5 and SHA-512.
- Application uses network_mode: host for Docker networking.
