/* ============================================
   CAMERA HANDLER — Attendance Recognition
   Face Recognition Attendance System
   ============================================ */

let videoStream = null;
let recognitionInterval = null;
let isRecognizing = false;
let recognizedCount = 0;
let unknownCount = 0;
let duplicateCount = 0;
let notifiedStudents = new Set();

const RECOGNITION_INTERVAL_MS = 2000; // Process every 2 seconds

document.addEventListener('DOMContentLoaded', function () {
  const video = document.getElementById('videoElement');
  const canvas = document.getElementById('canvasOverlay');
  const ctx = canvas ? canvas.getContext('2d') : null;
  const startBtn = document.getElementById('startCameraBtn');
  const stopBtn = document.getElementById('stopCameraBtn');
  const captureBtn = document.getElementById('captureBtn');
  const resultsPanel = document.getElementById('resultsPanel');
  const statusIndicator = document.getElementById('statusIndicator');

  // Only initialise if camera elements exist on the page
  if (!video) return;

  if (startBtn) startBtn.addEventListener('click', startCamera);
  if (stopBtn) stopBtn.addEventListener('click', stopCamera);
  if (captureBtn) captureBtn.addEventListener('click', captureAndRecognize);

  /* ===========================
     Start Camera
     =========================== */
  async function startCamera() {
    try {
      videoStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        }
      });

      video.srcObject = videoStream;
      await video.play();

      // Size canvas to match video
      if (canvas) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
      }

      // Toggle button visibility
      if (startBtn) startBtn.style.display = 'none';
      if (stopBtn) stopBtn.style.display = 'inline-flex';
      if (captureBtn) captureBtn.style.display = 'inline-flex';

      // Status indicator
      if (statusIndicator) {
        statusIndicator.innerHTML = '<span class="status-dot online"></span> Camera Active';
      }

      isRecognizing = true;
      recognitionInterval = setInterval(captureAndRecognize, RECOGNITION_INTERVAL_MS);

      if (typeof showToast === 'function') {
        showToast('Camera started. Recognition active.', 'info');
      }
    } catch (err) {
      if (typeof showToast === 'function') {
        showToast('Camera access denied: ' + err.message, 'danger');
      }
      console.error('Camera error:', err);
    }
  }

  /* ===========================
     Stop Camera
     =========================== */
  function stopCamera() {
    isRecognizing = false;

    if (recognitionInterval) {
      clearInterval(recognitionInterval);
      recognitionInterval = null;
    }

    if (videoStream) {
      videoStream.getTracks().forEach(function (track) {
        track.stop();
      });
      videoStream = null;
    }

    video.srcObject = null;

    if (ctx) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    
    // Clear the notified set so if they restart camera, it can notify again
    notifiedStudents.clear();

    if (startBtn) startBtn.style.display = 'inline-flex';
    if (stopBtn) stopBtn.style.display = 'none';
    if (captureBtn) captureBtn.style.display = 'none';

    if (statusIndicator) {
      statusIndicator.innerHTML = '<span class="status-dot offline"></span> Camera Off';
    }

    if (typeof showToast === 'function') {
      showToast('Camera stopped.', 'info');
    }
  }

  /* ===========================
     Capture & Recognize
     =========================== */
  async function captureAndRecognize() {
    if (!isRecognizing || !video.srcObject) return;

    // Capture frame to an off-screen canvas
    var captureCanvas = document.createElement('canvas');
    captureCanvas.width = video.videoWidth;
    captureCanvas.height = video.videoHeight;
    var captureCtx = captureCanvas.getContext('2d');
    captureCtx.drawImage(video, 0, 0);

    var base64 = captureCanvas.toDataURL('image/jpeg', 0.8).split(',')[1];

    try {
      var csrfMeta = document.querySelector('meta[name="csrf-token"]');
      var csrfToken = csrfMeta ? csrfMeta.content : '';

      var response = await fetch('/attendance/recognize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ frame: base64 })
      });

      var data = await response.json();

      // Draw bounding boxes on overlay canvas
      if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (data.faces && data.faces.length > 0) {
          data.faces.forEach(function (result) {
            if (result.known) {
              drawResult(ctx, result);
            }
          });
        }
      }

      // Update results panel
      if (data.faces && data.faces.length > 0) {
        data.faces.forEach(function (result) {
          if (result.known) {
            addResultItem(result);
          }
        });
      }

      // Update counters
      updateCounters();
    } catch (err) {
      console.error('Recognition error:', err);
    }
  }

  /* ===========================
     Draw Bounding Box Result
     =========================== */
  function drawResult(ctx, result) {
    if (!result.location || result.location.length < 4) return;

    var top = result.location[0];
    var right = result.location[1];
    var bottom = result.location[2];
    var left = result.location[3];

    var color = result.known ? '#34C759' : '#FF3B30';
    var glowColor = result.known ? 'rgba(52,199,89,0.3)' : 'rgba(255,59,48,0.3)';

    // Glow effect
    ctx.shadowColor = glowColor;
    ctx.shadowBlur = 15;

    // Bounding box with rounded corners
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;

    var r = 8;
    var x = left;
    var y = top;
    var w = right - left;
    var h = bottom - top;

    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.arcTo(x + w, y, x + w, y + r, r);
    ctx.lineTo(x + w, y + h - r);
    ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
    ctx.lineTo(x + r, y + h);
    ctx.arcTo(x, y + h, x, y + h - r, r);
    ctx.lineTo(x, y + r);
    ctx.arcTo(x, y, x + r, y, r);
    ctx.closePath();
    ctx.stroke();

    // Reset shadow for label
    ctx.shadowBlur = 0;
    ctx.shadowColor = 'transparent';

    // Label pill
    var confidence = result.confidence != null ? result.confidence : 0;
    var label = result.known
      ? (result.name || 'Known') + ' (' + confidence + '%)'
      : 'Unknown (' + confidence + '%)';

    ctx.font = '600 13px Inter, sans-serif';
    var textWidth = ctx.measureText(label).width;
    var pillWidth = textWidth + 20;
    var pillHeight = 26;
    var pillX = left;
    var pillY = top - pillHeight - 6;

    // Clamp pill position to canvas
    if (pillY < 0) pillY = bottom + 6;

    // Pill background
    ctx.fillStyle = result.known ? 'rgba(52,199,89,0.85)' : 'rgba(255,59,48,0.85)';
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(pillX, pillY, pillWidth, pillHeight, pillHeight / 2);
    } else {
      // Fallback for browsers without roundRect
      var pr = pillHeight / 2;
      ctx.moveTo(pillX + pr, pillY);
      ctx.lineTo(pillX + pillWidth - pr, pillY);
      ctx.arcTo(pillX + pillWidth, pillY, pillX + pillWidth, pillY + pr, pr);
      ctx.arcTo(pillX + pillWidth, pillY + pillHeight, pillX + pillWidth - pr, pillY + pillHeight, pr);
      ctx.lineTo(pillX + pr, pillY + pillHeight);
      ctx.arcTo(pillX, pillY + pillHeight, pillX, pillY + pillHeight - pr, pr);
      ctx.arcTo(pillX, pillY, pillX + pr, pillY, pr);
      ctx.closePath();
    }
    ctx.fill();

    // Pill text
    ctx.fillStyle = '#fff';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, pillX + 10, pillY + pillHeight / 2);
  }

  /* ===========================
     Add Result Item to Panel
     =========================== */
  function addResultItem(result) {
    var panel = document.getElementById('resultsPanel');
    if (!panel) return;

    // Avoid spamming the same student multiple times in one session
    if (result.known && result.student_id) {
      if (notifiedStudents.has(result.student_id)) {
        return; 
      }
      notifiedStudents.add(result.student_id);
    }

    // Remove empty state
    var emptyState = panel.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    // Determine status
    var statusClass, statusIcon, statusColor;

    if (result.known) {
      if (result.status === 'already_marked') {
        statusClass = 'duplicate';
        statusIcon = 'bi-clock-fill';
        statusColor = 'var(--spatial-orange)';
        duplicateCount++;
      } else {
        statusClass = 'recognized';
        statusIcon = 'bi-check-circle-fill';
        statusColor = 'var(--spatial-green)';
        recognizedCount++;
      }
    } else {
      statusClass = 'unknown';
      statusIcon = 'bi-x-circle-fill';
      statusColor = 'var(--spatial-red)';
      unknownCount++;
    }

    var confidence = result.confidence != null ? result.confidence : 0;
    var item = document.createElement('div');
    item.className = 'result-item ' + statusClass;
    item.innerHTML =
      '<i class="bi ' + statusIcon + '" style="font-size: 20px; color: ' + statusColor + ';"></i>' +
      '<div style="flex: 1;">' +
        '<div style="font-weight: 600;">' + escapeHtml(result.name || 'Unknown Face') + '</div>' +
        '<div style="font-size: 12px; color: var(--spatial-text-secondary);">' +
          escapeHtml(result.roll_number || '') +
          (result.department ? ' &bull; ' + escapeHtml(result.department) : '') +
        '</div>' +
      '</div>' +
      '<div style="text-align: right;">' +
        '<div style="font-weight: 600; color: ' + statusColor + ';">' + confidence + '%</div>' +
        '<div style="font-size: 11px; color: var(--spatial-text-tertiary);">' + new Date().toLocaleTimeString() + '</div>' +
      '</div>';

    panel.insertBefore(item, panel.firstChild);

    // Show toast notification
    if (typeof showToast === 'function') {
      if (result.known && result.status === 'marked') {
        showToast('✅ Attendance marked for ' + (result.name || 'student'), 'success');
      } else if (result.status === 'already_marked') {
        showToast('⏰ ' + (result.name || 'Student') + ' already marked today', 'warning');
      } else if (!result.known) {
        showToast('❌ Unknown face detected', 'danger');
      }
    }
  }

  /* ===========================
     Update Stat Counters
     =========================== */
  function updateCounters() {
    var rc = document.getElementById('recognizedCount');
    var uc = document.getElementById('unknownCount');
    var dc = document.getElementById('duplicateCount');
    if (rc) rc.textContent = recognizedCount;
    if (uc) uc.textContent = unknownCount;
    if (dc) dc.textContent = duplicateCount;
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
     Cleanup on Page Unload
     =========================== */
  window.addEventListener('beforeunload', function () {
    if (videoStream) {
      videoStream.getTracks().forEach(function (track) {
        track.stop();
      });
    }
    if (recognitionInterval) {
      clearInterval(recognitionInterval);
    }
  });
});
