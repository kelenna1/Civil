/* =============================================================================
   CandlesDown — App Engine
   Countdown timers, modals, dropdowns, confetti, accessibility
   ============================================================================= */

(function () {
  'use strict';

  // ═══════════════════════════════════════════════
  // Countdown Timer (requestAnimationFrame)
  // ═══════════════════════════════════════════════

  let lastTick = 0;

  function tick(timestamp) {
    // Only update once per second
    if (timestamp - lastTick >= 1000 || lastTick === 0) {
      lastTick = timestamp;
      updateCountdowns();
    }
    requestAnimationFrame(tick);
  }

  function updateCountdowns() {
    const now = new Date();

    // Hero countdown
    const hero = document.querySelector('[data-hero-date]');
    if (hero) {
      const target = new Date(hero.dataset.heroDate + 'T00:00:00');
      const diff = target - now;
      if (diff > 0) {
        updateUnit(hero, 'days', Math.floor(diff / 86400000));
        updateUnit(hero, 'hours', Math.floor((diff % 86400000) / 3600000));
        updateUnit(hero, 'minutes', Math.floor((diff % 3600000) / 60000));
        updateUnit(hero, 'seconds', Math.floor((diff % 60000) / 1000));
      }
    }

    // Card countdowns
    document.querySelectorAll('[data-card-date]').forEach(function (card) {
      const target = new Date(card.dataset.cardDate + 'T00:00:00');
      const diff = target - now;
      if (diff > 0) {
        updateUnit(card, 'days', Math.floor(diff / 86400000));
        updateUnit(card, 'hours', Math.floor((diff % 86400000) / 3600000));
        updateUnit(card, 'minutes', Math.floor((diff % 3600000) / 60000));
        updateUnit(card, 'seconds', Math.floor((diff % 60000) / 1000));
      }
    });
  }

  function updateUnit(container, unit, value) {
    var el = container.querySelector('[data-unit="' + unit + '"]');
    if (!el) return;
    var padded = String(value).padStart(2, '0');
    if (el.textContent !== padded) {
      el.textContent = padded;
      el.style.transform = 'scale(1.08)';
      el.style.transition = 'transform 0.15s ease-out';
      setTimeout(function () { el.style.transform = 'scale(1)'; }, 150);
    }
  }

  requestAnimationFrame(tick);

  // ═══════════════════════════════════════════════
  // Dropdown Toggle
  // ═══════════════════════════════════════════════

  document.addEventListener('click', function (e) {
    var trigger = e.target.closest('.dropdown__trigger');
    if (trigger) {
      e.stopPropagation();
      var menu = trigger.nextElementSibling;
      document.querySelectorAll('.dropdown__menu.is-open').forEach(function (m) {
        if (m !== menu) m.classList.remove('is-open');
      });
      menu.classList.toggle('is-open');
      return;
    }
    // Close all dropdowns
    document.querySelectorAll('.dropdown__menu.is-open').forEach(function (m) {
      m.classList.remove('is-open');
    });
  });

  // ═══════════════════════════════════════════════
  // Modal — Focus Trap & Accessibility
  // ═══════════════════════════════════════════════

  function openModal(modal) {
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    // Store last focused element
    modal._lastFocus = document.activeElement;
    // Focus first focusable element
    var first = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (first) first.focus();
    trapFocus(modal);
  }

  function closeModal(modal) {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    if (modal._lastFocus) modal._lastFocus.focus();
  }

  function trapFocus(modal) {
    modal._trapHandler = function (e) {
      if (e.key !== 'Tab') return;
      var focusable = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
      if (focusable.length === 0) return;
      var first = focusable[0];
      var last = focusable[focusable.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    modal.addEventListener('keydown', modal._trapHandler);
  }

  // Escape closes modals
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.is-open').forEach(function (m) {
        closeModal(m);
      });
    }
  });

  // Expose globally for onclick handlers in templates
  window.openModal = function (id) {
    var m = document.getElementById(id);
    if (m) openModal(m);
  };
  window.closeModal = function (id) {
    var m = document.getElementById(id);
    if (m) closeModal(m);
  };

  // Click overlay to close
  document.querySelectorAll('.modal-overlay').forEach(function (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeModal(overlay);
    });
    // Set initial ARIA
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-hidden', 'true');
  });

  // ═══════════════════════════════════════════════
  // Toast Auto-Dismiss
  // ═══════════════════════════════════════════════

  document.querySelectorAll('.toast').forEach(function (toast) {
    setTimeout(function () { toast.remove(); }, 7000);
  });

  // ═══════════════════════════════════════════════
  // Confetti — Birthday Celebration 🎉
  // ═══════════════════════════════════════════════

  function spawnConfetti() {
    var container = document.createElement('div');
    container.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:9998;overflow:hidden;';
    document.body.appendChild(container);

    var colors = ['#f59e0b', '#fbbf24', '#8b5cf6', '#a78bfa', '#10b981', '#ef4444', '#f97316', '#ec4899'];

    for (var i = 0; i < 60; i++) {
      var piece = document.createElement('div');
      var color = colors[Math.floor(Math.random() * colors.length)];
      var size = Math.random() * 8 + 4;
      var left = Math.random() * 100;
      var delay = Math.random() * 2;
      var duration = Math.random() * 2 + 2;

      piece.style.cssText =
        'position:absolute;' +
        'top:-10px;' +
        'left:' + left + '%;' +
        'width:' + size + 'px;' +
        'height:' + size + 'px;' +
        'background:' + color + ';' +
        'border-radius:' + (Math.random() > 0.5 ? '50%' : '2px') + ';' +
        'opacity:0.9;' +
        'animation:confetti-fall ' + duration + 's ease-in ' + delay + 's forwards;';

      container.appendChild(piece);
    }

    // Clean up after animation
    setTimeout(function () { container.remove(); }, 5000);
  }

  // Inject confetti keyframes
  var style = document.createElement('style');
  style.textContent =
    '@keyframes confetti-fall {' +
    '0% { transform: translateY(0) rotate(0deg); opacity: 1; }' +
    '100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }' +
    '}';
  document.head.appendChild(style);

  // Trigger confetti if there's a birthday today
  if (document.querySelector('.birthday-card--today') || document.querySelector('.hero-countdown--today')) {
    setTimeout(spawnConfetti, 800);
  }

})();
