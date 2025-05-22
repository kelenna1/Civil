document.addEventListener('DOMContentLoaded', function() {
  // Initialize main countdown
  const mainCountdown = document.querySelector('.countdown-timer');
  if (mainCountdown) {
    initCountdown(mainCountdown, true);
  }

  // Initialize mini countdowns
  document.querySelectorAll('.birthday-card').forEach(card => {
    initCountdown(card, false);
  });

  function initCountdown(container, isMain) {
    const dateStr = container.dataset.countdownDate;
    if (!dateStr) return;

    const targetDate = new Date(dateStr + 'T00:00:00');
    const prefix = isMain ? 'countdown-value' : 'mini-countdown-value';
    
    const daysEl = container.querySelector(`.${prefix}.days`);
    const hoursEl = container.querySelector(`.${prefix}.hours`);
    const minsEl = container.querySelector(`.${prefix}.minutes`);
    const secsEl = container.querySelector(`.${prefix}.seconds`);

    function update() {
      const now = new Date();
      const diff = targetDate - now;

      if (diff <= 0) {
        if (!isMain) {
          container.classList.add('birthday-today');
          const infoEl = container.querySelector('.upcoming-info');
          if (infoEl) infoEl.textContent = "🎉 Today's the day!";
        }
        setValue(daysEl, '0');
        setValue(hoursEl, '0');
        setValue(minsEl, '0');
        setValue(secsEl, '0');
        return;
      }

      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
      const minutes = Math.floor((diff / (1000 * 60)) % 60);
      const seconds = Math.floor((diff / 1000) % 60);

      setValue(daysEl, days);
      setValue(hoursEl, hours.toString().padStart(2, '0'));
      if (minsEl) setValue(minsEl, minutes.toString().padStart(2, '0'));
      if (secsEl) setValue(secsEl, seconds.toString().padStart(2, '0'));
    }

    function setValue(el, value) {
      if (el) el.textContent = value;
    }

    update();
    setInterval(update, 1000);
  }
});