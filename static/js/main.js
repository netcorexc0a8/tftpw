function copyToClipboard(text, event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  
  // Try modern API first
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      showToast("Copied: " + text);
    }).catch(err => {
      fallbackCopy(text);
    });
  } else {
    fallbackCopy(text);
  }
}

function fallbackCopy(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.position = "fixed";
  textarea.style.left = "-9999px";
  textarea.style.top = "0";
  document.body.appendChild(textarea);
  textarea.select();
  try {
    const success = document.execCommand("copy");
    if (success) {
      showToast("Copied: " + text);
    } else {
      alert("Failed to copy to clipboard");
    }
  } catch (err) {
    alert("Failed to copy to clipboard: " + err);
  }
  document.body.removeChild(textarea);
}

function showToast(message) {
  const toast = document.createElement("div");
  toast.textContent = message;
  toast.style.cssText = "position: fixed; bottom: 20px; right: 20px; background: #10a37f; color: white; padding: 10px 20px; border-radius: 5px; z-index: 1000; animation: fadeIn 0.3s;";
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2000);
}

// Add click event listeners to elements with data-copy-text attribute
document.addEventListener('DOMContentLoaded', function() {
  const copyElements = document.querySelectorAll('[data-copy-text]');
  
  copyElements.forEach(function(element) {
    element.addEventListener('click', function(event) {
      const text = element.getAttribute('data-copy-text');
      try {
        const parsedText = JSON.parse(text);
        copyToClipboard(parsedText, event);
      } catch (e) {
        copyToClipboard(text, event);
      }
    });
  });

  const form = document.getElementById("upload-form");
  const fileInput = document.getElementById("file-upload");
  const selectedFilesList = document.getElementById("selected-files-list");
  const progressContainer = document.getElementById("progress-container");
  const progressBar = document.getElementById("progress-bar");
  const progressText = document.getElementById("progress-text");
  
  // Get max_size_mb from data attribute
  const maxSizeMb = parseInt(document.body.getAttribute('data-max-size-mb') || '500');

  fileInput.addEventListener("change", () => {
    selectedFilesList.innerHTML = "";
    const maxSize = maxSizeMb * 1024 * 1024;
    let hasLargeFile = false;
    Array.from(fileInput.files).forEach(file => {
      if (file.size > maxSize) {
        alert(`File ${file.name} is too large (maximum ${maxSizeMb} MB)`);
        hasLargeFile = true;
        return;
      }
      const sizeText = file.size < 1024 * 1024
        ? `${Math.round(file.size / 1024)} KB`
        : `${Math.round(file.size / (1024 * 1024))} MB`;
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
    if (hasLargeFile) {
      fileInput.value = "";
      selectedFilesList.innerHTML = "";
    }
  });

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
      const fileProgressContainer = fileDiv.querySelector('.file-progress-container');
      const fileProgressBar = fileProgressContainer.querySelector('.file-progress-bar');
      const fileProgressText = fileProgressContainer.querySelector('.file-progress-text');

      fileProgressContainer.style.display = "block";

      xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
          const percent = (e.loaded / e.total) * 100;
          fileProgressBar.style.width = percent + "%";
          fileProgressText.textContent = Math.round(percent) + "%";
        }
      };

      xhr.onload = function() {
        if (xhr.status === 200) {
          fileProgressBar.style.width = "100%";
          fileProgressText.textContent = "Calculating hashes...";
          completed++;
          if (completed === files.length) {
            setTimeout(() => location.reload(), 2000);
          }
        } else if (xhr.status === 413) {
          alert("File " + file.name + " is too large (maximum " + maxSizeMb + " MB)");
        } else {
          alert("Error uploading " + file.name + " (status: " + xhr.status + ")");
        }
      };

      xhr.send(formData);
    });
  });

  const style = document.createElement("style");
  style.textContent = `
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `;
  document.head.appendChild(style);
});
