(() => {
  'use strict';

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- header / progress / to-top ---------- */
  const header = $('#siteHeader');
  const progressBar = $('#progressBar');
  const toTop = $('#toTop');
  const heroBg = $('#heroBg');

  let ticking = false;
  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(() => {
      const y = window.scrollY || window.pageYOffset;
      const doc = document.documentElement;
      const max = doc.scrollHeight - window.innerHeight;
      const pct = max > 0 ? Math.min(100, (y / max) * 100) : 0;

      if (progressBar) progressBar.style.width = pct + '%';
      if (header) header.classList.toggle('is-solid', y > 36);
      if (toTop) toTop.classList.toggle('is-visible', y > 720);

      if (heroBg && !reduceMotion && window.innerWidth > 720) {
        heroBg.style.transform = `translate3d(0, ${Math.min(y * 0.16, 120)}px, 0) scale(1.04)`;
      }
      updateActiveNav(y);
      ticking = false;
    });
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- mobile menu ---------- */
  const menuToggle = $('#menuToggle');
  const mainNav = $('#mainNav');

  const closeMenu = () => {
    document.body.classList.remove('nav-open');
    if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
  };

  if (menuToggle && mainNav) {
    menuToggle.addEventListener('click', () => {
      const open = document.body.classList.toggle('nav-open');
      menuToggle.setAttribute('aria-expanded', String(open));
    });
    $$('a', mainNav).forEach((link) => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeMenu();
    });
    window.addEventListener('resize', () => {
      if (window.innerWidth > 900) closeMenu();
    });
  }

  /* ---------- reveal on scroll ---------- */
  const revealItems = $$('.reveal');
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    revealItems.forEach((el) => io.observe(el));
  } else {
    revealItems.forEach((el) => el.classList.add('is-visible'));
  }

  /* ---------- animated counters ---------- */
  const counters = $$('[data-count]');
  const formatNumber = (value, decimals) => {
    return value.toLocaleString('ru-RU', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    });
  };

  const animateCounter = (el) => {
    const target = parseFloat(el.dataset.count);
    const decimals = parseInt(el.dataset.decimals || '0', 10);
    const prefix = el.dataset.prefix || '';
    const suffix = el.dataset.suffix || '';
    const valueEl = el.querySelector('.stat-value, .stat-big') || el;
    const duration = reduceMotion ? 0 : 1500;
    const start = performance.now();

    const tick = (now) => {
      const t = duration === 0 ? 1 : Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      const value = target * eased;
      valueEl.textContent = prefix + formatNumber(value, decimals) + suffix;
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  if ('IntersectionObserver' in window) {
    const co = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          co.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach((el) => co.observe(el));
  } else {
    counters.forEach(animateCounter);
  }

  /* ---------- active nav ---------- */
  const navLinks = $$('#mainNav a');
  const sections = $$('[data-section]');

  function updateActiveNav(y) {
    if (!sections.length) return;
    let current = '';
    const offset = 140;
    sections.forEach((section) => {
      const top = section.offsetTop;
      if (y + offset >= top) current = section.id;
    });
    navLinks.forEach((link) => {
      const href = link.getAttribute('href');
      link.classList.toggle('is-current', href === '#' + current);
    });
  }

  /* ---------- layer explorer ---------- */
  const layerButtons = $$('.layer-btn');
  const layerPanels = $$('[data-layer-panel]');

  function activateLayer(index) {
    layerButtons.forEach((btn, i) => {
      const active = i === index;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-selected', String(active));
      btn.tabIndex = active ? 0 : -1;
    });
    layerPanels.forEach((panel, i) => {
      const active = i === index;
      panel.hidden = !active;
      panel.classList.toggle('is-active', active);
    });
  }

  layerButtons.forEach((btn, i) => {
    btn.addEventListener('click', () => activateLayer(i));
    btn.addEventListener('keydown', (e) => {
      if (!['ArrowDown', 'ArrowRight', 'ArrowUp', 'ArrowLeft'].includes(e.key)) return;
      e.preventDefault();
      let next = i;
      if (e.key === 'ArrowDown' || e.key === 'ArrowRight') next = (i + 1) % layerButtons.length;
      if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') next = (i - 1 + layerButtons.length) % layerButtons.length;
      activateLayer(next);
      layerButtons[next].focus();
    });
  });

  /* ---------- scenarios ---------- */
  const scenarioButtons = $$('.scenario-btn');
  const scenarioPanels = $$('[data-scenario-panel]');

  function activateScenario(index) {
    scenarioButtons.forEach((btn, i) => {
      const active = i === index;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-selected', String(active));
      btn.tabIndex = active ? 0 : -1;
    });
    scenarioPanels.forEach((panel, i) => {
      const active = i === index;
      panel.hidden = !active;
      panel.classList.toggle('is-active', active);
    });
  }

  scenarioButtons.forEach((btn, i) => {
    btn.addEventListener('click', () => activateScenario(i));
    btn.addEventListener('keydown', (e) => {
      if (!['ArrowDown', 'ArrowRight', 'ArrowUp', 'ArrowLeft'].includes(e.key)) return;
      e.preventDefault();
      let next = i;
      if (e.key === 'ArrowDown' || e.key === 'ArrowRight') next = (i + 1) % scenarioButtons.length;
      if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') next = (i - 1 + scenarioButtons.length) % scenarioButtons.length;
      activateScenario(next);
      scenarioButtons[next].focus();
    });
  });

  /* ---------- source filters ---------- */
  const filterButtons = $$('.filter-btn');
  const sourceCards = $$('.source-card');

  filterButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;
      filterButtons.forEach((b) => b.classList.toggle('is-active', b === btn));
      sourceCards.forEach((card) => {
        const show = filter === 'all' || card.dataset.cat === filter;
        card.classList.toggle('is-hidden', !show);
        if (show) card.classList.add('is-visible');
      });
    });
  });

  /* ---------- audio waveform / custom player ---------- */
  const audio = $('#ambientAudio');
  const waveform = $('#waveform');
  const audioToggle = $('#audioToggle');
  const audioIcon = $('#audioIcon');
  const audioTrack = $('#audioTrack');
  const audioFill = $('#audioFill');
  const audioTime = $('#audioTime');
  let audioDuration = 48;

  const fmtTime = (value) => {
    const sec = Math.max(0, Math.floor(value || 0));
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${String(s).padStart(2, '0')}`;
  };

  const updateAudioUI = () => {
    if (!audio) return;
    const duration = Number.isFinite(audio.duration) && audio.duration > 0 ? audio.duration : audioDuration;
    const current = Math.min(audio.currentTime || 0, duration);
    const pct = duration ? (current / duration) * 100 : 0;
    if (audioFill) audioFill.style.width = pct + '%';
    if (audioTime) audioTime.textContent = `${fmtTime(current)} / ${fmtTime(duration)}`;
    if (audioTrack) {
      audioTrack.setAttribute('aria-valuemax', String(Math.round(duration)));
      audioTrack.setAttribute('aria-valuenow', String(Math.round(current)));
    }
  };

  if (waveform) {
    for (let i = 0; i < 56; i += 1) {
      const bar = document.createElement('span');
      const h = 18 + Math.random() * 78;
      bar.style.height = h + '%';
      bar.style.animationDelay = (i * 0.035) + 's';
      bar.style.animationDuration = (0.75 + Math.random() * 0.8) + 's';
      waveform.appendChild(bar);
    }
    waveform.style.cursor = 'pointer';
    waveform.addEventListener('click', () => {
      if (!audio) return;
      if (audio.paused) audio.play().catch(() => {});
      else audio.pause();
    });
  }

  if (audio) {
    audio.volume = 0.8;
    audio.addEventListener('loadedmetadata', () => {
      if (Number.isFinite(audio.duration) && audio.duration > 0) audioDuration = audio.duration;
      updateAudioUI();
    });
    audio.addEventListener('timeupdate', updateAudioUI);
    audio.addEventListener('play', () => {
      if (waveform) waveform.classList.add('is-playing');
      if (audioIcon) audioIcon.textContent = '❚❚';
      if (audioToggle) audioToggle.setAttribute('aria-label', 'Пауза');
    });
    audio.addEventListener('pause', () => {
      if (waveform) waveform.classList.remove('is-playing');
      if (audioIcon) audioIcon.textContent = '▶';
      if (audioToggle) audioToggle.setAttribute('aria-label', 'Воспроизвести аудио');
    });
    audio.addEventListener('ended', () => {
      if (waveform) waveform.classList.remove('is-playing');
      if (audioIcon) audioIcon.textContent = '▶';
      if (audioToggle) audioToggle.setAttribute('aria-label', 'Воспроизвести аудио');
      updateAudioUI();
    });
    updateAudioUI();
  }

  if (audioToggle && audio) {
    audioToggle.addEventListener('click', () => {
      if (audio.paused) audio.play().catch(() => {});
      else audio.pause();
    });
  }

  if (audioTrack && audio) {
    const seek = (clientX) => {
      const rect = audioTrack.getBoundingClientRect();
      const ratio = Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));
      const duration = Number.isFinite(audio.duration) && audio.duration > 0 ? audio.duration : audioDuration;
      audio.currentTime = ratio * duration;
      updateAudioUI();
    };
    audioTrack.addEventListener('click', (e) => seek(e.clientX));
    audioTrack.addEventListener('keydown', (e) => {
      const duration = Number.isFinite(audio.duration) && audio.duration > 0 ? audio.duration : audioDuration;
      if (e.key === 'ArrowRight') {
        e.preventDefault();
        audio.currentTime = Math.min(duration, audio.currentTime + 5);
        updateAudioUI();
      }
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        audio.currentTime = Math.max(0, audio.currentTime - 5);
        updateAudioUI();
      }
      if (e.key === ' ' || e.key === 'Enter') {
        e.preventDefault();
        if (audio.paused) audio.play().catch(() => {}); else audio.pause();
      }
    });
  }

  /* ---------- back to top ---------- */
  if (toTop) {
    toTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }

  /* ---------- smooth anchors fallback ---------- */
  $$('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (e) => {
      const id = link.getAttribute('href');
      if (!id || id === '#') return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      closeMenu();
      const top = target.getBoundingClientRect().top + window.scrollY - 86;
      window.scrollTo({ top, behavior: reduceMotion ? 'auto' : 'smooth' });
      try { history.replaceState(null, '', id); } catch (e) { /* file:// */ }
    });
  });
})();
