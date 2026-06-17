// ─────────────────────────────────────────────────────────────────
//  SSLC EXAMINATION MARCH 2026 — Student Details Form Script
//  Drop this script after the #form div is present in the DOM.
// ─────────────────────────────────────────────────────────────────

(function () {

  /* ── 1. Render the initial form ───────────────────────────────── */
  function renderForm(prefill = {}) {
    document.getElementById('form').innerHTML = `
      <div id="content-header">SSLC EXAMINATION MARCH 2026 <br> STUDENT DETAILS FORM</div>
      <div class="warning-bar">
        <span>WARNING:</span> Students are requested to fill the below form carefully without
        committing any mistakes. If any mistakes are committed the details cannot be changed.
      </div>
      <div class="form-container">
        <form id="student-form">
          <div id="box-header">STUDENT DETAILS</div>
          <hr>

          <div class="input-box">
            <input type="text" name="name" id="name" required placeholder=" "
                   value="${prefill.name || ''}" />
            <label for="name">Name</label>
          </div>

          <div class="input-box">
            <input type="text" name="reg_no" id="regno" required placeholder=" "
                   value="${prefill.reg_no || ''}" />
            <label for="regno">SSLC Register Number</label>
          </div>

          <div class="input-box">
            <input type="date" name="dob" id="dob" required placeholder=" "
                   value="${prefill.dob || ''}" />
            <label for="dob">Select DOB</label>
          </div>

          <div class="input-box">
            <div class="field-wrap">
              <select name="sec" id="sec-select" required>
                <option value="" disabled ${!prefill.sec ? 'selected' : ''} hidden></option>
                <option value="A" ${prefill.sec === 'A' ? 'selected' : ''}>X - A</option>
                <option value="B" ${prefill.sec === 'B' ? 'selected' : ''}>X - B</option>
                <option value="C" ${prefill.sec === 'C' ? 'selected' : ''}>X - C</option>
                <option value="D" ${prefill.sec === 'D' ? 'selected' : ''}>X - D</option>
                <option value="E" ${prefill.sec === 'E' ? 'selected' : ''}>X - E</option>
              </select>
              <label>Select Class</label>
            </div>
          </div>

          <div id="error-msg" style="display:none; color:red; text-align:center;
               padding:8px; margin:8px 0; border:1px solid red; border-radius:4px;
               font-size:0.9em;"></div>

          <div class="btn">
            <button type="submit" id="login-btn">PREVIEW →</button>
          </div>
        </form>
      </div>`;

    document.getElementById('student-form').addEventListener('submit', handleFormSubmit);
  }

  /* ── 2. Collect form values ───────────────────────────────────── */
  function collectForm() {
    const f      = document.getElementById('student-form');
    const name   = f.querySelector('#name').value.trim();
    const reg_no = f.querySelector('#regno').value.trim();
    const dob    = f.querySelector('#dob').value;
    const sec    = f.querySelector('#sec-select').value;
    return { name, reg_no, dob, sec };
  }

  function showError(msg) {
    const el = document.getElementById('error-msg');
    el.textContent = msg;
    el.style.display = 'block';
  }

  function hideError() {
    const el = document.getElementById('error-msg');
    if (el) { el.style.display = 'none'; el.textContent = ''; }
  }

  /* ── 3. Handle form submit → show preview ─────────────────────── */
  function handleFormSubmit(e) {
    e.preventDefault();
    hideError();

    const form = document.getElementById('student-form');

    // Rely on native HTML5 validation (no novalidate on this form)
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    const data = collectForm();
    renderPreview(data);
  }

  /* ── 4. Render preview screen ─────────────────────────────────── */
  function renderPreview(data) {
    const dobFormatted = data.dob
      ? new Date(data.dob).toLocaleDateString('en-IN', { day:'2-digit', month:'long', year:'numeric' })
      : '—';

    document.getElementById('form').innerHTML = `
      <div id="content-header">SSLC EXAMINATION MARCH 2026 <br> STUDENT DETAILS FORM</div>
      <div class="form-container">
        <div id="box-header">📋 Preview — Verify Your Details</div>
        <hr>

        <table class="preview-table">
          <tbody>
            <tr><th>Name</th><td>${escHtml(data.name)}</td></tr>
            <tr><th>Register No.</th><td>${escHtml(data.reg_no)}</td></tr>
            <tr><th>Date of Birth</th><td>${dobFormatted}</td></tr>
            <tr><th>Class</th><td>X - ${escHtml(data.sec)}</td></tr>
          </tbody>
        </table>

        <div style="display:flex;gap:12px;justify-content:center;margin-top:24px;flex-wrap:wrap;">
          <button id="edit-btn"  class="btn-secondary">✏️ Edit Details</button>
          <button id="final-btn" class="btn-primary">  ✅ Final Submit</button>
        </div>
      </div>

      <!-- Confirmation Dialog -->
      <div id="confirm-overlay" style="display:none;">
        <div id="confirm-dialog">
          <button id="dialog-close" title="Close">✕</button>
          <div id="dialog-icon">⚠️</div>
          <h3>Are you sure?</h3>
          <p>Once submitted, your details <strong>cannot be changed</strong>.<br>
             Please confirm that all the information is correct.</p>
          <div style="display:flex;gap:12px;justify-content:center;margin-top:20px;">
            <button id="dialog-cancel" class="btn-secondary">Cancel</button>
            <button id="dialog-ok"     class="btn-primary">OK, Submit</button>
          </div>
        </div>
      </div>`;

    document.getElementById('edit-btn').addEventListener('click', () => renderForm(data));

    document.getElementById('final-btn').addEventListener('click', () => {
      document.getElementById('confirm-overlay').style.display = 'flex';
    });

    const closeDialog = () => {
      document.getElementById('confirm-overlay').style.display = 'none';
    };

    document.getElementById('dialog-close').addEventListener('click',  closeDialog);
    document.getElementById('dialog-cancel').addEventListener('click', closeDialog);
    document.getElementById('confirm-overlay').addEventListener('click', function (e) {
      if (e.target === this) closeDialog();   // click outside dialog box
    });

    document.getElementById('dialog-ok').addEventListener('click', () => {
      closeDialog();
      submitToBackend(data);
    });
  }

  /* ── 5. POST to Flask ─────────────────────────────────────────── */
  async function submitToBackend(data) {
    const overlay = createLoadingOverlay();
    document.getElementById('form').appendChild(overlay);

    const formData = new FormData();
    Object.entries(data).forEach(([k, v]) => formData.append(k, v));

    try {
      const response = await fetch('/submit/sslc', {
        method: 'POST',
        body: formData,
      });

      overlay.remove();
      const result = await response.json();

      if (response.ok) {
        renderSuccess(result, data);
      } else {
        renderPreview(data);                   // restore preview
        setTimeout(() => {
          const isDuplicate = result.detail && result.detail.includes('already exists');
          alert(isDuplicate
            ? '⚠️ This Register Number has already been submitted.'
            : (result.detail || 'Submission failed. Please try again.'));
        }, 100);
      }
    } catch (err) {
      overlay.remove();
      renderPreview(data);
      setTimeout(() => alert('❌ Network error. Please check your connection.'), 100);
    }
  }

  /* ── 6. Success screen ────────────────────────────────────────── */
  function renderSuccess(result, data) {
    document.getElementById('form').innerHTML = `
      <div id="content-header">SSLC EXAMINATION MARCH 2026 <br> STUDENT DETAILS FORM</div>
      <div class="form-container">
        <div id="box-header">✅ Submitted Successfully</div>
        <hr>
        <div style="text-align:center;padding:28px 16px;line-height:2;">
          <div style="font-size:17px">Your details have been recorded successfully.</div>
          <strong>${escHtml(result.name || data.name)}</strong><br>
          <span style="color:#555;">Register No: ${escHtml(result.reg_no || data.reg_no)}</span>
        </div>
      </div>`;
  }

  /* ── 7. Helpers ───────────────────────────────────────────────── */
  function escHtml(str) {
    return String(str)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function createLoadingOverlay() {
    const el = document.createElement('div');
    el.id = 'loading-overlay';
    el.innerHTML = `<div id="loading-box"><div class="spinner"></div>Submitting…</div>`;
    return el;
  }

  /* ── 8. Inject required CSS ──────────────────────────────────── */
  const style = document.createElement('style');
  style.textContent = `
    /* ── Preview table ── */
    .preview-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      font-size: 14px;
    }
    .preview-table th, .preview-table td {
      padding: 10px 14px;
      border-bottom: 1px solid #e0e0e0;
      text-align: left;
    }
    .preview-table th {
      color: #555;
      font-weight: 600;
      width: 38%;
      background: #f7f9fc;
    }
    .preview-table td { color: #1a1a1a; }

    /* ── Buttons ── */
    .btn-primary, .btn-secondary {
      padding: 10px 26px;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: opacity .2s, transform .1s;
    }
    .btn-primary  { background: #1a73e8; color: #fff; }
    .btn-secondary{ background: #f0f0f0; color: #333; }
    .btn-primary:hover  { opacity: .9; }
    .btn-secondary:hover{ background: #e2e2e2; }
    .btn-primary:active,
    .btn-secondary:active { transform: scale(.97); }

    /* ── Confirmation dialog ── */
    #confirm-overlay {
      position: fixed; inset: 0;
      background: rgba(0,0,0,.45);
      display: flex; align-items: center; justify-content: center;
      z-index: 9999;
    }
    #confirm-dialog {
      background: #fff;
      border-radius: 12px;
      padding: 36px 32px 28px;
      max-width: 380px; width: 90%;
      text-align: center;
      position: relative;
      box-shadow: 0 8px 32px rgba(0,0,0,.18);
      animation: dialogIn .2s ease;
    }
    @keyframes dialogIn {
      from { transform: scale(.92); opacity: 0; }
      to   { transform: scale(1);   opacity: 1; }
    }
    #dialog-close {
      position: absolute; top: 12px; right: 14px;
      background: none; border: none;
      font-size: 18px; cursor: pointer; color: #888;
      line-height: 1; padding: 2px 6px;
      border-radius: 50%;
      transition: background .15s;
    }
    #dialog-close:hover { background: #f0f0f0; color: #333; }
    #dialog-icon { font-size: 42px; margin-bottom: 8px; }
    #confirm-dialog h3 { margin: 0 0 8px; font-size: 18px; color: #1a1a1a; }
    #confirm-dialog p  { margin: 0; font-size: 14px; color: #555; line-height: 1.6; }

    /* ── Loading overlay ── */
    #loading-overlay {
      position: fixed; inset: 0;
      background: rgba(255,255,255,.75);
      display: flex; align-items: center; justify-content: center;
      z-index: 8888;
    }
    #loading-box {
      display: flex; align-items: center; gap: 12px;
      background: #fff; padding: 20px 32px;
      border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,.12);
      font-size: 15px; font-weight: 600; color: #333;
    }
    .spinner {
      width: 22px; height: 22px;
      border: 3px solid #e0e0e0;
      border-top-color: #1a73e8;
      border-radius: 50%;
      animation: spin .7s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  `;
  document.head.appendChild(style);

  /* ── 9. Kick off ──────────────────────────────────────────────── */
  renderForm();

})();