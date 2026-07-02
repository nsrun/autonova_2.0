/* ═══════════════════════════════════════════════════════
   AutoNova — Professional JS v2.0
   ═══════════════════════════════════════════════════════ */

'use strict';

/* ── 1. NAVBAR SCROLL ─────────────────────────────────── */
(function () {
  const nav = document.getElementById('navbar') || document.querySelector('.an-navbar');
  if (!nav) return;
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 40);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();

/* ── 2. HAMBURGER MENU ────────────────────────────────── */
(function () {
  const btn  = document.getElementById('hamburger') || document.querySelector('.an-hamburger');
  const menu = document.getElementById('mobileMenu') || document.querySelector('.an-mobile-menu');
  if (!btn || !menu) return;

  btn.addEventListener('click', () => {
    btn.classList.toggle('open');
    menu.classList.toggle('open');
    btn.setAttribute('aria-expanded', btn.classList.contains('open'));
  });

  // Close on link click
  menu.querySelectorAll('a, .an-nav-link').forEach(a =>
    a.addEventListener('click', () => {
      btn.classList.remove('open');
      menu.classList.remove('open');
    })
  );

  // Close on outside click
  document.addEventListener('click', e => {
    if (!btn.contains(e.target) && !menu.contains(e.target)) {
      btn.classList.remove('open');
      menu.classList.remove('open');
    }
  });
})();

/* ── 3. ACTIVE NAV LINK ───────────────────────────────── */
(function () {
  const path = window.location.pathname;
  document.querySelectorAll('.an-nav-link[href]').forEach(a => {
    const href = a.getAttribute('href');
    if (href === path || (href !== '/' && path.startsWith(href))) {
      a.classList.add('active');
    }
  });
})();

/* ── 4. SCROLL REVEAL ─────────────────────────────────── */
(function () {
  const els = document.querySelectorAll('.an-reveal, .reveal');
  if (!els.length) return;

  const obs = new IntersectionObserver(entries => {
    entries.forEach(({ isIntersecting, target }) => {
      if (isIntersecting) {
        target.classList.add('visible');
        obs.unobserve(target);
      }
    });
  }, { threshold: 0.08 });

  els.forEach(el => obs.observe(el));
})();

/* ── 5. COUNTER ANIMATION ─────────────────────────────── */
(function () {
  const counters = document.querySelectorAll('.an-counter, [data-counter]');
  if (!counters.length) return;

  function animateCount(el) {
    const target = parseInt(el.dataset.target || el.textContent, 10);
    if (isNaN(target)) return;
    const suffix = el.dataset.suffix || '';
    const prefix = el.dataset.prefix || '';
    let cur = 0;
    const step = Math.ceil(target / 60);
    const iv = setInterval(() => {
      cur = Math.min(cur + step, target);
      el.textContent = prefix + cur.toLocaleString('en-IN') + suffix;
      if (cur >= target) clearInterval(iv);
    }, 20);
  }

  const obs = new IntersectionObserver(entries => {
    entries.forEach(({ isIntersecting, target }) => {
      if (!isIntersecting || target.dataset.counted) return;
      target.dataset.counted = '1';
      animateCount(target);
      obs.unobserve(target);
    });
  }, { threshold: 0.5 });

  counters.forEach(el => obs.observe(el));
})();

/* ── 6. SMOOTH SCROLL ─────────────────────────────────── */
(function () {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href');
      if (id === '#' || id === '#!') return;
      const target = document.querySelector(id);
      if (target) {
        e.preventDefault();
        const top = target.getBoundingClientRect().top + window.scrollY - 80;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });
})();

/* ── 7. IMAGE GALLERY (detail pages) ─────────────────── */
(function () {
  const mainImg = document.getElementById('mainImage');
  if (!mainImg) return;

  document.querySelectorAll('.an-gallery-thumb').forEach(thumb => {
    thumb.addEventListener('click', function () {
      mainImg.src = this.src;
      document.querySelectorAll('.an-gallery-thumb').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
    });
  });
})();

/* ── 8. PASSWORD TOGGLE ───────────────────────────────── */
(function () {
  document.querySelectorAll('.toggle-pwd').forEach(btn => {
    btn.addEventListener('click', function () {
      const wrap = this.closest('.position-relative');
      const inp  = wrap ? wrap.querySelector('input') : null;
      const icon = this.querySelector('i');
      if (!inp) return;
      const isHidden = inp.type === 'password';
      inp.type = isHidden ? 'text' : 'password';
      if (icon) icon.className = isHidden ? 'bi bi-eye-slash' : 'bi bi-eye';
    });
  });
})();

/* ── 9. IMAGE UPLOAD PREVIEW ──────────────────────────── */
(function () {
  const zone    = document.getElementById('uploadZone');
  const input   = document.getElementById('imageInput');
  const preview = document.getElementById('imagePreview');
  if (!zone || !input || !preview) return;

  zone.addEventListener('click', e => {
    if (e.target !== input) input.click();
  });
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault(); zone.classList.remove('drag-over');
    renderPreviews(e.dataTransfer.files);
  });
  input.addEventListener('change', () => renderPreviews(input.files));

  function renderPreviews(files) {
    preview.innerHTML = '';
    Array.from(files).forEach((file, i) => {
      const reader = new FileReader();
      reader.onload = ev => {
        const wrap = document.createElement('div');
        wrap.className = 'an-preview-thumb';
        wrap.innerHTML = `<img src="${ev.target.result}" alt="Preview">
          ${i === 0 ? '<span class="an-primary-badge">Main</span>' : ''}`;
        preview.appendChild(wrap);
      };
      reader.readAsDataURL(file);
    });
  }
})();

/* ── 10. CANVAS PARTICLE BG (hero) ───────────────────── */
(function () {
  const canvas = document.getElementById('hero-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let W, H;

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }
  resize();
  window.addEventListener('resize', resize, { passive: true });

  const DOTS = Array.from({ length: 55 }, () => ({
    x: Math.random(), y: Math.random(),
    r: Math.random() * 1.8 + 0.4,
    vx: (Math.random() - 0.5) * 0.00026,
    vy: (Math.random() - 0.5) * 0.00026,
    a: Math.random() * 0.3 + 0.07,
    va: (Math.random() - 0.5) * 0.004,
    c: Math.random() > 0.5 ? 'rgba(37,99,235,' : 'rgba(212,175,55,',
  }));

  let mx = 0.5, my = 0.5;
  canvas.addEventListener('mousemove', e => {
    const r = canvas.getBoundingClientRect();
    mx = (e.clientX - r.left) / r.width;
    my = (e.clientY - r.top) / r.height;
  }, { passive: true });

  function drawLine(a, b) {
    const dx = (a.x - b.x) * W, dy = (a.y - b.y) * H;
    const d  = Math.sqrt(dx * dx + dy * dy);
    if (d > 130) return;
    ctx.beginPath();
    ctx.moveTo(a.x * W, a.y * H);
    ctx.lineTo(b.x * W, b.y * H);
    ctx.strokeStyle = `rgba(37,99,235,${(1 - d / 130) * 0.06})`;
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  (function loop() {
    ctx.clearRect(0, 0, W, H);
    DOTS.forEach(d => {
      d.vx += (mx - d.x) * 0.000005;
      d.vy += (my - d.y) * 0.000005;
      d.x += d.vx; d.y += d.vy; d.a += d.va;
      if (d.x < 0 || d.x > 1) d.vx *= -1;
      if (d.y < 0 || d.y > 1) d.vy *= -1;
      if (d.a < 0.04 || d.a > 0.42) d.va *= -1;
      ctx.beginPath();
      ctx.arc(d.x * W, d.y * H, d.r, 0, Math.PI * 2);
      ctx.fillStyle = d.c + d.a + ')';
      ctx.fill();
    });
    for (let i = 0; i < DOTS.length; i++)
      for (let j = i + 1; j < DOTS.length; j++)
        drawLine(DOTS[i], DOTS[j]);
    requestAnimationFrame(loop);
  })();
})();

/* ── 11. AUTO-DISMISS ALERTS ──────────────────────────── */
(function () {
  document.querySelectorAll('.alert-dismissible').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity .4s, transform .4s';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-6px)';
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });
})();

/* ── 12. TOOLTIP INIT (Bootstrap) ────────────────────── */
(function () {
  if (typeof bootstrap === 'undefined') return;
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el, { trigger: 'hover' });
  });
})();