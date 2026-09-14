/* ============================================================
   Pendakian Lawu — main.js
   Global JS: sidebar, flash, modals, progress bars, formatting,
   form validation, table search, confirmations
   ============================================================ */

'use strict';

// ── Sidebar toggle (mobile) ────────────────────────────────
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if (!sidebar) return;
  const isOpen = sidebar.classList.toggle('open');
  if (overlay) overlay.classList.toggle('hidden', !isOpen);
}

function closeSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if (sidebar) sidebar.classList.remove('open');
  if (overlay) overlay.classList.add('hidden');
}

// Close sidebar when a nav link is tapped on mobile
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.sidebar-nav a').forEach(link =>
    link.addEventListener('click', () => {
      if (window.innerWidth <= 768) closeSidebar();
    })
  );
});

// ── Flash auto-dismiss ─────────────────────────────────────
function autoDismissFlash() {
  document.querySelectorAll('.flash').forEach((el, i) => {
    setTimeout(() => {
      el.style.transition = 'opacity .45s, transform .45s';
      el.style.opacity    = '0';
      el.style.transform  = 'translateX(120%)';
      setTimeout(() => el.remove(), 450);
    }, 4500 + i * 350);
  });
}

// ── Inline toast (programmatic flash) ─────────────────────
function showToast(message, type = 'info') {
  const container = document.getElementById('flashContainer');
  if (!container) return;

  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
  const div   = document.createElement('div');
  div.className = `flash flash-${type}`;
  div.setAttribute('role', 'alert');
  div.innerHTML =
    `<span>${icons[type] ?? 'ℹ️'}</span>` +
    `<span>${message}</span>` +
    `<button class="flash-close" aria-label="Tutup" onclick="this.parentElement.remove()">✕</button>`;
  container.appendChild(div);

  setTimeout(() => {
    div.style.transition = 'opacity .4s, transform .4s';
    div.style.opacity    = '0';
    div.style.transform  = 'translateX(120%)';
    setTimeout(() => div.remove(), 400);
  }, 4500);
}

// ── Modal helpers ──────────────────────────────────────────
function openModal(id) {
  const overlay = document.getElementById(id);
  if (!overlay) return;
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
  // Focus first focusable element inside modal
  const focusable = overlay.querySelector('input,textarea,select,button:not(.modal-close)');
  if (focusable) focusable.focus();
}

function closeModal(id) {
  const overlay = document.getElementById(id);
  if (!overlay) return;
  overlay.classList.remove('open');
  document.body.style.overflow = '';
}

// Click on backdrop closes the modal
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
    document.body.style.overflow = '';
  }
});

// Escape key closes all open modals
document.addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  document.querySelectorAll('.modal-overlay.open').forEach(m => {
    m.classList.remove('open');
    document.body.style.overflow = '';
  });
});

// ── Animated progress bars ─────────────────────────────────
function animateProgressBars() {
  document.querySelectorAll('.progress-bar-fill[data-width]').forEach(bar => {
    const target = Math.min(parseFloat(bar.dataset.width) || 0, 100);
    bar.style.width = '0%';
    // Double rAF ensures the initial 0% paint happens first
    requestAnimationFrame(() => requestAnimationFrame(() => {
      bar.style.width = target + '%';
    }));
  });
}

// ── Currency formatter (Indonesian Rupiah) ─────────────────
function formatRupiah(num) {
  return 'Rp\u00a0' + Number(num).toLocaleString('id-ID');
}

// Apply to all [data-rupiah] elements on page
function applyRupiahFormat() {
  document.querySelectorAll('[data-rupiah]').forEach(el => {
    const val = parseFloat(el.dataset.rupiah);
    if (!isNaN(val)) el.textContent = formatRupiah(val);
  });
}

// ── Table live-search ──────────────────────────────────────
/**
 * setupTableSearch(inputId, tableId)
 * Filters table rows as the user types.
 */
function setupTableSearch(inputId, tableId) {
  const input = document.getElementById(inputId);
  const table = document.getElementById(tableId);
  if (!input || !table) return;

  function doFilter() {
    const q = input.value.toLowerCase().trim();
    let visibleCount = 0;
    table.querySelectorAll('tbody tr').forEach(row => {
      const match = !q || row.textContent.toLowerCase().includes(q);
      row.style.display = match ? '' : 'none';
      if (match) visibleCount++;
    });

    // Show/hide "no results" row
    let emptyRow = table.querySelector('tr.no-results');
    if (!visibleCount && q) {
      if (!emptyRow) {
        const cols = table.querySelectorAll('thead th').length;
        emptyRow = document.createElement('tr');
        emptyRow.className = 'no-results';
        emptyRow.innerHTML =
          `<td colspan="${cols}" style="text-align:center;padding:24px;color:var(--gray-400);">` +
          `Tidak ada hasil untuk "<strong>${escapeHtml(q)}</strong>"</td>`;
        table.querySelector('tbody').appendChild(emptyRow);
      }
    } else if (emptyRow) {
      emptyRow.remove();
    }
  }

  input.addEventListener('input', doFilter);
}

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, c =>
    ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])
  );
}

// ── Confirm-action helper ──────────────────────────────────
function confirmAction(message) {
  return window.confirm(message ?? 'Apakah kamu yakin?');
}

// ── Number-input formatting (savings form) ─────────────────
/**
 * Attaches a display formatter to a numeric input so the user
 * sees a formatted preview below the field as they type.
 */
function setupAmountPreview(inputId, previewId) {
  const input   = document.getElementById(inputId);
  const preview = document.getElementById(previewId);
  if (!input) return;

  function update() {
    const raw = parseFloat(input.value);
    if (preview) {
      preview.textContent = isNaN(raw) || raw <= 0 ? '' : '= ' + formatRupiah(raw);
    }
  }

  input.addEventListener('input', update);
  update();
}

// ── Form validation ────────────────────────────────────────
/**
 * Validates all [required] fields in a form.
 * Highlights invalid fields and returns false if any are empty.
 */
function validateForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return true;

  let valid = true;
  form.querySelectorAll('[required]').forEach(field => {
    const empty = !field.value.trim();
    field.style.borderColor = empty ? 'var(--danger)' : '';
    if (empty) valid = false;
  });

  if (!valid) showToast('Semua field yang wajib diisi (*) harus diisi.', 'error');
  return valid;
}

// Re-clear error highlight when the user starts typing
document.addEventListener('input', e => {
  if (e.target.style && e.target.style.borderColor === 'var(--danger)') {
    if (e.target.value.trim()) e.target.style.borderColor = '';
  }
}, true);

// ── Savings form — client-side submit guard ────────────────
function initSavingForm() {
  const form = document.getElementById('savingForm');
  if (!form) return;

  form.addEventListener('submit', function (e) {
    const amountInput = form.querySelector('#amount');
    if (!amountInput) return;

    const val = parseFloat(amountInput.value);
    if (isNaN(val) || val <= 0) {
      e.preventDefault();
      amountInput.style.borderColor = 'var(--danger)';
      amountInput.focus();
      showToast('Masukkan jumlah tabungan yang valid (lebih dari 0).', 'error');
    }
  });
}

// ── Participant form — password strength hint ──────────────
function initPasswordStrength() {
  const pwInput = document.getElementById('password');
  if (!pwInput) return;

  const hint = document.createElement('div');
  hint.className = 'form-hint';
  hint.id        = 'pwStrengthHint';
  pwInput.parentNode.insertBefore(hint, pwInput.nextSibling);

  pwInput.addEventListener('input', () => {
    const v = pwInput.value;
    if (!v) { hint.textContent = ''; return; }
    const score =
      (v.length >= 8 ? 1 : 0) +
      (/[A-Z]/.test(v)    ? 1 : 0) +
      (/[0-9]/.test(v)    ? 1 : 0) +
      (/[^A-Za-z0-9]/.test(v) ? 1 : 0);

    const levels = [
      { text: '⚠️ Sangat lemah',  color: 'var(--danger)' },
      { text: '⚠️ Lemah',         color: 'var(--danger)' },
      { text: '🟡 Cukup',         color: 'var(--warning)' },
      { text: '✅ Kuat',          color: 'var(--success)' },
      { text: '💪 Sangat kuat',   color: 'var(--success)' },
    ];
    const { text, color } = levels[score] ?? levels[0];
    hint.textContent  = text;
    hint.style.color  = color;
    hint.style.fontWeight = '600';
  });
}

// ── Active nav-link marker ─────────────────────────────────
function markActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.sidebar-nav a').forEach(link => {
    link.classList.remove('active');
    const href = link.getAttribute('href');
    // Exact match OR path starts with href (for sub-pages), but avoid '/'
    if (href && href !== '/' && path.startsWith(href)) {
      link.classList.add('active');
    } else if (href === path) {
      link.classList.add('active');
    }
  });
}

// ── Number input — prevent accidental mouse-wheel changes ──
document.addEventListener('wheel', e => {
  if (document.activeElement && document.activeElement.type === 'number') {
    document.activeElement.blur();
  }
}, { passive: true });

// ── Route-form: dynamic content placeholder ───────────────
function updateContentHint() {
  const typeSelect = document.getElementById('item_type');
  const hint       = document.getElementById('contentHint');
  const textarea   = document.getElementById('content');
  if (!typeSelect) return;

  const map = {
    checkpoint: {
      hint: 'Tulis deskripsi kondisi pos, fasilitas, air, dll.',
      placeholder: 'Contoh: Pos ini memiliki sumber air dan area camp yang luas.',
    },
    note: {
      hint: 'Tulis catatan penting untuk para pendaki.',
      placeholder: 'Contoh: Jangan tinggalkan sampah di sini. Larangan api unggun.',
    },
    image: {
      hint: 'Masukkan URL gambar yang dapat diakses publik (https://...).',
      placeholder: 'https://example.com/foto-pos.jpg',
    },
    map_link: {
      hint: 'Masukkan link Google Maps, Wikiloc, atau peta lainnya.',
      placeholder: 'https://maps.google.com/...',
    },
  };

  const entry = map[typeSelect.value] ?? map.checkpoint;
  if (hint)    hint.textContent     = entry.hint;
  if (textarea) textarea.placeholder = entry.placeholder;
}

// ── DOMContentLoaded — wire everything up ─────────────────
document.addEventListener('DOMContentLoaded', () => {
  autoDismissFlash();
  animateProgressBars();
  applyRupiahFormat();
  markActiveNav();
  initSavingForm();
  initPasswordStrength();
  setupAmountPreview('amount', 'amountPreview');

  // Table search (participants page)
  setupTableSearch('searchInput', 'participantsTable');

  // Route-form dynamic hints
  const itemTypeSelect = document.getElementById('item_type');
  if (itemTypeSelect) {
    itemTypeSelect.addEventListener('change', updateContentHint);
    updateContentHint(); // run once on load
  }

  // Confirm-delete forms: attach generic confirm to any form with data-confirm
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', e => {
      if (!confirmAction(form.dataset.confirm)) e.preventDefault();
    });
  });
});
