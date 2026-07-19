/* ============================================
   FACE REGISTRATION — Webcam Capture & Upload
   Face Recognition Attendance System
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {
  var video = document.getElementById('webcamVideo');
  var captureBtn = document.getElementById('captureBtn');
  var startCameraBtn = document.getElementById('startCameraBtn');
  var stopCameraBtn = document.getElementById('stopCameraBtn');
  var uploadInput = document.getElementById('fileInput');
  var dropzone = document.getElementById('dropZone');
  var capturedGrid = document.getElementById('capturedImages');
  var registerBtn = document.getElementById('registerBtn');
  var statusMsg = document.getElementById('statusArea');
  var capturedImages = [];
  var stream = null;

  // Only initialise if registration elements exist
  if (!video && !dropzone) return;

  if (startCameraBtn) startCameraBtn.addEventListener('click', startWebcam);
  if (stopCameraBtn) stopCameraBtn.addEventListener('click', stopWebcam);

  /* ===========================
     Start Webcam
     =========================== */
  async function startWebcam() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        }
      });

      if (video) {
        video.srcObject = stream;
        video.play();
      }
      if (startCameraBtn) startCameraBtn.disabled = true;
      if (captureBtn) captureBtn.disabled = false;
      if (stopCameraBtn) stopCameraBtn.disabled = false;
    } catch (err) {
      console.error('Webcam error:', err);
      if (typeof showToast === 'function') {
        showToast('Webcam access denied: ' + err.message, 'danger');
      }
    }
  }

  function stopWebcam() {
    if (stream) {
      stream.getTracks().forEach(function(track) { track.stop(); });
      stream = null;
    }
    if (video) video.srcObject = null;
    if (startCameraBtn) startCameraBtn.disabled = false;
    if (captureBtn) captureBtn.disabled = true;
    if (stopCameraBtn) stopCameraBtn.disabled = true;
  }

  // Automatically start webcam if video element exists
  if (video) {
    startWebcam();
  }

  /* ===========================
     Capture from Webcam
     =========================== */
  if (captureBtn) {
    captureBtn.addEventListener('click', function () {
      if (!video || !video.srcObject) {
        if (typeof showToast === 'function') {
          showToast('Webcam is not active', 'warning');
        }
        return;
      }

      var captureCanvas = document.createElement('canvas');
      captureCanvas.width = video.videoWidth;
      captureCanvas.height = video.videoHeight;
      var captureCtx = captureCanvas.getContext('2d');
      captureCtx.drawImage(video, 0, 0);
      var dataUrl = captureCanvas.toDataURL('image/jpeg', 0.9);

      capturedImages.push(dataUrl);
      addToGrid(dataUrl);

      if (typeof showToast === 'function') {
        showToast('Image captured! (' + capturedImages.length + ' total)', 'success');
      }

      if (registerBtn) {
        registerBtn.disabled = false;
      }

      updateCaptureCount();
    });
  }

  /* ===========================
     Drag and Drop
     =========================== */
  if (dropzone) {
    dropzone.addEventListener('dragover', function (e) {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('drag-over');
    });

    dropzone.addEventListener('dragleave', function (e) {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('drag-over');
    });

    dropzone.addEventListener('drop', function (e) {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('drag-over');
      handleFiles(e.dataTransfer.files);
    });

    dropzone.addEventListener('click', function () {
      if (uploadInput) uploadInput.click();
    });
  }

  if (uploadInput) {
    uploadInput.addEventListener('change', function (e) {
      handleFiles(e.target.files);
      // Reset input so re-selecting the same file still triggers change
      uploadInput.value = '';
    });
  }

  /* ===========================
     File Handling
     =========================== */
  function handleFiles(files) {
    Array.from(files).forEach(function (file) {
      if (!file.type.startsWith('image/')) {
        if (typeof showToast === 'function') {
          showToast('Skipped non-image file: ' + file.name, 'warning');
        }
        return;
      }

      // Limit file size to 10MB
      if (file.size > 10 * 1024 * 1024) {
        if (typeof showToast === 'function') {
          showToast('File too large: ' + file.name + ' (max 10MB)', 'warning');
        }
        return;
      }

      var reader = new FileReader();
      reader.onload = function (e) {
        capturedImages.push(e.target.result);
        addToGrid(e.target.result);

        if (registerBtn) {
          registerBtn.disabled = false;
        }

        updateCaptureCount();
      };
      reader.readAsDataURL(file);
    });
  }

  /* ===========================
     Grid Management
     =========================== */
  function addToGrid(dataUrl) {
    if (!capturedGrid) return;

    // Remove empty state if present
    var emptyState = capturedGrid.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    var wrapper = document.createElement('div');
    wrapper.style.position = 'relative';

    var img = document.createElement('img');
    img.src = dataUrl;
    img.alt = 'Captured face image';

    // Remove button
    var removeBtn = document.createElement('button');
    removeBtn.innerHTML = '&times;';
    removeBtn.style.cssText =
      'position:absolute;top:4px;right:4px;width:24px;height:24px;border-radius:50%;' +
      'background:rgba(255,59,48,0.85);color:#fff;border:none;cursor:pointer;' +
      'font-size:14px;display:flex;align-items:center;justify-content:center;' +
      'opacity:0;transition:opacity 0.2s;';

    wrapper.addEventListener('mouseenter', function () {
      removeBtn.style.opacity = '1';
    });
    wrapper.addEventListener('mouseleave', function () {
      removeBtn.style.opacity = '0';
    });

    removeBtn.addEventListener('click', function () {
      var index = Array.from(capturedGrid.children).indexOf(wrapper);
      if (index > -1) {
        capturedImages.splice(index, 1);
      }
      wrapper.remove();
      updateCaptureCount();

      if (capturedImages.length === 0 && registerBtn) {
        registerBtn.disabled = true;
      }
    });

    wrapper.appendChild(img);
    wrapper.appendChild(removeBtn);
    capturedGrid.appendChild(wrapper);
  }

  function updateCaptureCount() {
    var countEl = document.getElementById('captureCount');
    if (countEl) {
      countEl.textContent = capturedImages.length;
    }
  }

  /* ===========================
     Register Face
     =========================== */
  if (registerBtn) {
    registerBtn.addEventListener('click', async function () {
      if (capturedImages.length === 0) {
        if (typeof showToast === 'function') {
          showToast('Please capture or upload at least one image', 'warning');
        }
        return;
      }

      // Get student ID from the page (set as data attribute or global)
      var sid = typeof studentId !== 'undefined' ? studentId : registerBtn.dataset.studentId;
      if (!sid) {
        if (typeof showToast === 'function') {
          showToast('Student ID not found', 'danger');
        }
        return;
      }

      registerBtn.disabled = true;
      var originalHTML = registerBtn.innerHTML;
      registerBtn.innerHTML =
        '<span class="spatial-spinner" style="width:16px;height:16px;border-width:2px;"></span> Registering...';

      try {
        var csrfMeta = document.querySelector('meta[name="csrf-token"]');
        var csrfToken = csrfMeta ? csrfMeta.content : '';

        // Send the most recently captured image
        var imageData = capturedImages[capturedImages.length - 1].split(',')[1];

        var response = await fetch('/students/register-face/' + sid, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
          },
          body: JSON.stringify({ image_data: imageData })
        });

        var data = await response.json();

        if (data.success) {
          if (typeof showToast === 'function') {
            showToast(data.message || 'Face registered successfully!', 'success');
          }
          if (statusMsg) {
            statusMsg.innerHTML =
              '<i class="bi bi-check-circle-fill" style="color: var(--spatial-green);"></i> ' +
              escapeHtml(data.message || 'Face registered successfully!');
            statusMsg.style.color = 'var(--spatial-green)';
          }
        } else {
          if (typeof showToast === 'function') {
            showToast(data.message || 'Registration failed', 'danger');
          }
          if (statusMsg) {
            statusMsg.innerHTML =
              '<i class="bi bi-x-circle-fill" style="color: var(--spatial-red);"></i> ' +
              escapeHtml(data.message || 'Registration failed');
            statusMsg.style.color = 'var(--spatial-red)';
          }
        }
      } catch (err) {
        console.error('Registration error:', err);
        if (typeof showToast === 'function') {
          showToast('Error: ' + err.message, 'danger');
        }
        if (statusMsg) {
          statusMsg.innerHTML =
            '<i class="bi bi-x-circle-fill" style="color: var(--spatial-red);"></i> Error: ' +
            escapeHtml(err.message);
          statusMsg.style.color = 'var(--spatial-red)';
        }
      } finally {
        registerBtn.disabled = false;
        registerBtn.innerHTML = originalHTML || '<i class="bi bi-person-check"></i> Register Face';
      }
    });
  }

  /* ===========================
     Utility: Escape HTML
     =========================== */
  function escapeHtml(text) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(text || ''));
    return div.innerHTML;
  }

  /* ===========================
     Cleanup on Page Leave
     =========================== */
  window.addEventListener('beforeunload', function () {
    if (stream) {
      stream.getTracks().forEach(function (track) {
        track.stop();
      });
    }
  });
});
