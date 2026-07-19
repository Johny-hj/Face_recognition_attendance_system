/* ============================================
   DASHBOARD — Charts & Stats
   Face Recognition Attendance System
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ===========================
     visionOS Color Palette
     =========================== */
  var colors = {
    blue: '#007AFF',
    green: '#34C759',
    red: '#FF3B30',
    orange: '#FF9500',
    purple: '#AF52DE',
    teal: '#5AC8FA',
    pink: '#FF2D55',
    indigo: '#5856D6'
  };

  /**
   * Convert hex colour to rgba string.
   * @param {string} hex - Hex colour code (e.g. '#007AFF')
   * @param {number} alpha - Opacity (0-1)
   * @returns {string} rgba string
   */
  function colorAlpha(hex, alpha) {
    var r = parseInt(hex.slice(1, 3), 16);
    var g = parseInt(hex.slice(3, 5), 16);
    var b = parseInt(hex.slice(5, 7), 16);
    return 'rgba(' + r + ',' + g + ',' + b + ',' + alpha + ')';
  }

  /* ===========================
     Chart.js Global Defaults
     =========================== */
  if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = "'Inter', system-ui, -apple-system, sans-serif";
    Chart.defaults.color = getComputedStyle(document.documentElement)
      .getPropertyValue('--spatial-text-secondary').trim() || '#6e6e73';
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0,0,0,0.8)';
    Chart.defaults.plugins.tooltip.cornerRadius = 12;
    Chart.defaults.plugins.tooltip.padding = { top: 10, right: 14, bottom: 10, left: 14 };
    Chart.defaults.plugins.tooltip.titleFont = { weight: '600', size: 13 };
    Chart.defaults.plugins.tooltip.bodyFont = { size: 12 };
  }

  /* ===========================
     Weekly Attendance Chart
     =========================== */
  var weeklyCtx = document.getElementById('weeklyChart');
  if (weeklyCtx && typeof weekData !== 'undefined' && typeof Chart !== 'undefined') {
    new Chart(weeklyCtx, {
      type: 'bar',
      data: {
        labels: weekData.map(function (d) { return d.date; }),
        datasets: [{
          label: 'Attendance',
          data: weekData.map(function (d) { return d.count; }),
          backgroundColor: colorAlpha(colors.blue, 0.6),
          borderColor: colors.blue,
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false,
          hoverBackgroundColor: colorAlpha(colors.blue, 0.8),
          hoverBorderColor: colors.blue
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              font: { family: 'Inter', size: 12 }
            },
            grid: {
              color: 'rgba(0,0,0,0.05)',
              drawBorder: false
            }
          },
          x: {
            ticks: {
              font: { family: 'Inter', size: 12 }
            },
            grid: { display: false }
          }
        },
        animation: {
          duration: 800,
          easing: 'easeOutQuart'
        }
      }
    });
  }

  /* ===========================
     Department Distribution Chart
     =========================== */
  var deptCtx = document.getElementById('deptChart');
  if (deptCtx && typeof deptData !== 'undefined' && typeof Chart !== 'undefined') {
    var deptColors = [
      colors.blue,
      colors.green,
      colors.purple,
      colors.orange,
      colors.teal,
      colors.pink,
      colors.red,
      colors.indigo
    ];

    new Chart(deptCtx, {
      type: 'doughnut',
      data: {
        labels: deptData.map(function (d) { return d.department; }),
        datasets: [{
          data: deptData.map(function (d) { return d.count; }),
          backgroundColor: deptData.map(function (_, i) {
            return colorAlpha(deptColors[i % deptColors.length], 0.7);
          }),
          borderColor: deptData.map(function (_, i) {
            return deptColors[i % deptColors.length];
          }),
          borderWidth: 2,
          hoverOffset: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 16,
              font: { family: 'Inter', size: 12 },
              usePointStyle: true,
              pointStyle: 'circle'
            }
          }
        },
        animation: {
          animateRotate: true,
          duration: 1000,
          easing: 'easeOutQuart'
        }
      }
    });
  }

  /* ===========================
     Monthly Trend Chart (optional)
     =========================== */
  var monthlyCtx = document.getElementById('monthlyChart');
  if (monthlyCtx && typeof monthlyData !== 'undefined' && typeof Chart !== 'undefined') {
    new Chart(monthlyCtx, {
      type: 'line',
      data: {
        labels: monthlyData.map(function (d) { return d.date; }),
        datasets: [{
          label: 'Attendance',
          data: monthlyData.map(function (d) { return d.count; }),
          borderColor: colors.blue,
          backgroundColor: colorAlpha(colors.blue, 0.1),
          borderWidth: 2.5,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 7,
          pointBackgroundColor: '#fff',
          pointBorderColor: colors.blue,
          pointBorderWidth: 2,
          pointHoverBackgroundColor: colors.blue,
          pointHoverBorderColor: '#fff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              font: { family: 'Inter', size: 12 }
            },
            grid: {
              color: 'rgba(0,0,0,0.05)',
              drawBorder: false
            }
          },
          x: {
            ticks: {
              font: { family: 'Inter', size: 12 },
              maxTicksLimit: 10
            },
            grid: { display: false }
          }
        },
        animation: {
          duration: 800,
          easing: 'easeOutQuart'
        }
      }
    });
  }

  /* ===========================
     Animate Stat Numbers
     =========================== */
  document.querySelectorAll('.stat-value').forEach(function (el) {
    var target = parseInt(el.textContent, 10);
    if (isNaN(target) || target === 0) return;

    var current = 0;
    var increment = Math.max(1, Math.ceil(target / 30));
    var suffix = el.dataset.suffix || '';

    // Store the target so we can start from 0
    el.textContent = '0' + suffix;

    var timer = setInterval(function () {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = current + suffix;
    }, 30);
  });

  /* ===========================
     Attendance Rate Ring (optional)
     =========================== */
  var rateRing = document.getElementById('attendanceRateRing');
  if (rateRing && typeof Chart !== 'undefined') {
    var rate = parseFloat(rateRing.dataset.rate) || 0;
    new Chart(rateRing, {
      type: 'doughnut',
      data: {
        datasets: [{
          data: [rate, 100 - rate],
          backgroundColor: [
            rate >= 80 ? colors.green : (rate >= 50 ? colors.orange : colors.red),
            'rgba(0,0,0,0.05)'
          ],
          borderWidth: 0,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '80%',
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false }
        },
        animation: {
          animateRotate: true,
          duration: 1200,
          easing: 'easeOutQuart'
        }
      }
    });
  }

});
