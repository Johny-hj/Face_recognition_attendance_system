/* ============================================
   MAIN APPLICATION JAVASCRIPT
   Face Recognition Attendance System
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ===========================
     1. Theme Toggle
     =========================== */

  const themeToggleBtn = document.getElementById('themeToggle');
  
  // The backend sets data-theme on the html tag.
  let currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
  
  // Resolve 'auto' theme based on OS preference
  if (currentTheme === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      currentTheme = prefersDark ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', currentTheme);
  }
  
  updateThemeIcon(currentTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function () {
      const activeTheme = document.documentElement.getAttribute('data-theme') || 'light';
      const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      updateThemeIcon(newTheme);
      if (typeof showToast === 'function') {
        showToast('Theme previewed. Save in Settings to persist.', 'info');
      }
    });
  }

  function updateThemeIcon(theme) {
    const icon = document.querySelector('#themeToggle i');
    if (!icon) return;
    if (theme === 'dark') {
      icon.className = 'bi bi-sun-fill';
    } else {
      icon.className = 'bi bi-moon-fill';
    }
  }


  /* ===========================
     2. Sidebar Toggle (Mobile)
     =========================== */

  const sidebarToggleBtn = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.spatial-sidebar');

  if (sidebarToggleBtn && sidebar) {
    sidebarToggleBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      sidebar.classList.toggle('show');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (e) {
      if (window.innerWidth <= 768 && sidebar.classList.contains('show')) {
        if (!sidebar.contains(e.target) && e.target !== sidebarToggleBtn) {
          sidebar.classList.remove('show');
        }
      }
    });

    // Close sidebar on escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && sidebar.classList.contains('show')) {
        sidebar.classList.remove('show');
      }
    });
  }


  /* ===========================
     3. Toast Auto-Hide
     =========================== */

  document.querySelectorAll('.spatial-toast[data-autohide]').forEach(function (toast) {
    const delay = parseInt(toast.getAttribute('data-autohide')) || 5000;
    setTimeout(function () {
      dismissToast(toast);
    }, delay);
  });

  // Close button on existing toasts
  document.querySelectorAll('.toast-close').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const toast = btn.closest('.spatial-toast');
      if (toast) dismissToast(toast);
    });
  });

  function dismissToast(toast) {
    toast.classList.add('toast-hiding');
    toast.addEventListener('animationend', function () {
      toast.remove();
    });
  }


  /* ===========================
     4. Global Toast Function
     =========================== */

  window.showToast = function (message, type) {
    type = type || 'info';

    // Ensure toast container exists
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    // Map type to icon
    var iconMap = {
      success: 'bi-check-circle-fill',
      danger: 'bi-x-circle-fill',
      error: 'bi-x-circle-fill',
      warning: 'bi-exclamation-triangle-fill',
      info: 'bi-info-circle-fill'
    };

    var icon = iconMap[type] || iconMap.info;

    var toast = document.createElement('div');
    toast.className = 'spatial-toast toast-' + type;
    toast.innerHTML =
      '<i class="bi ' + icon + '"></i>' +
      '<span style="flex:1;">' + escapeHtml(message) + '</span>' +
      '<button class="toast-close" aria-label="Close">&times;</button>';

    // Close button handler
    toast.querySelector('.toast-close').addEventListener('click', function () {
      dismissToast(toast);
    });

    container.appendChild(toast);

    // Auto-hide after 5 seconds
    setTimeout(function () {
      if (toast.parentNode) {
        dismissToast(toast);
      }
    }, 5000);
  };

  function escapeHtml(text) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
  }


  /* ===========================
     5. Loading Overlay
     =========================== */

  window.showLoading = function () {
    var overlay = document.getElementById('loadingOverlay');
    if (overlay) {
      overlay.style.display = 'flex';
    }
  };

  window.hideLoading = function () {
    var overlay = document.getElementById('loadingOverlay');
    if (overlay) {
      overlay.style.display = 'none';
    }
  };


  /* ===========================
     6. AJAX Helper
     =========================== */

  window.fetchAPI = async function (url, options) {
    options = options || {};

    // Add CSRF token
    var csrfMeta = document.querySelector('meta[name="csrf-token"]');
    var csrfToken = csrfMeta ? csrfMeta.content : null;
    if (csrfToken) {
      options.headers = Object.assign({}, options.headers || {}, {
        'X-CSRFToken': csrfToken
      });
    }

    // Show loading indicator
    showLoading();

    try {
      var response = await fetch(url, options);

      if (!response.ok) {
        var errorText = await response.text();
        throw new Error('Server error (' + response.status + '): ' + errorText);
      }

      return response;
    } catch (err) {
      showToast('Network error: ' + err.message, 'danger');
      throw err;
    } finally {
      hideLoading();
    }
  };


  /* ===========================
     7. Smooth Scroll for Anchors
     =========================== */

  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });


  /* ===========================
     8. Confirm Delete
     =========================== */

  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var message = form.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });

  // Also support confirm on individual buttons/links
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    if (el.tagName === 'FORM') return; // Already handled above
    el.addEventListener('click', function (e) {
      var message = el.getAttribute('data-confirm') || 'Are you sure?';
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });


  /* ===========================
     9. Landing Page Scroll Animations
     =========================== */

  var fadeElements = document.querySelectorAll('.fade-in-up');
  if (fadeElements.length > 0) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    fadeElements.forEach(function (el) {
      observer.observe(el);
    });
  }


  /* ===========================
     10. Active Sidebar Link
     =========================== */

  var currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-nav a').forEach(function (link) {
    var href = link.getAttribute('href');
    if (href && currentPath.startsWith(href) && href !== '/') {
      link.classList.add('active');
    } else if (href === '/' && currentPath === '/') {
      link.classList.add('active');
    }
  });

});
