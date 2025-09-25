# TFTPW v1.1.0

A web interface for managing a TFTPW server, built with Python Flask. Allows uploading, downloading, and deleting files with file hash display (MD5 and SHA-512) and upload progress bars.

---

## Features

- **Multiple file uploads** simultaneously.
- **File preview** with sizes displayed in MB (rounded to whole numbers) before upload.
- **File cards** with MD5 and SHA-512 hashes.
- **Download and Delete buttons** for each file.
- **Upload progress bar**.
- **Dark theme** interface.
- **File sorting** by name (case-insensitive).
- Maximum upload file size: configurable via `MAX_CONTENT_LENGTH` (default 500 MB).
- Full Docker compatibility.

---

## Requirements

- Docker and Docker Compose installed on your system.
- Ports 5000 (HTTP) and 69/UDP (TFTP) available.

---

## Environment Variables

The application uses environment variables for configuration. Create a `.env` file in the project root with the following variables:

- `SECRET_KEY`: A secret key used by Flask for session management and security. This should be a long, random string.
- `MAX_CONTENT_LENGTH`: Maximum file size for uploads in MB (default: 500).

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
- File sizes will be displayed in MB below the button.
- Click **⬆️ Upload** to send the files to the server.
- Uploaded files are listed as cards with:
  - File name
  - **⬇️ Download** and **🗑️ Delete** buttons
  - MD5 and SHA-512 hashes
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
- Progress bars show upload status in real-time.
- Supports concurrent file uploads from multiple users.
- TFTPW server runs as a daemon inside the Docker container alongside the Flask app.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.