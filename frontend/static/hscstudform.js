// ─────────────────────────────────────────────────────────────────
//  HSC (+2) EXAMINATION MARCH 2026 — Student Details Form Script
//  Drop this script after the #form div is present in the DOM.
//  Flask must expose the class-group data as a JS variable, e.g.:
//    <script>const CLASS_DATA = {{ class_data | tojson }};</script>
//  where class_data = [{"class":"A","groups":["csc","biomat"]}, …]
// ─────────────────────────────────────────────────────────────────

(function () {
  /* ── 1. Group code → display name map ─────────────────────────── */
  const GROUP_NAMES = {
    csc:    'COMPUTER SCIENCE / MATHS',
    biomat: 'BIOLOGY / MATHS',
    biocs:  'BIOLOGY / COMPUTER SCIENCE',
    artsca: 'ARTS / COMPUTER APPLICATION',
    artsbm: 'ARTS / BUSINESS MATHS',
    bme:    'BASIC MECHANICAL ENGINEERING / MATHS',
  };

  /* ── 2. Build class → groups lookup from Flask data ───────────── */
  // CLASS_DATA must be injected by Flask before this script runs.
  const classMap = {};           // { "A": ["csc","biomat"], … }
  (CLASS_DATA || []).forEach(item => {
    classMap[item.class] = item.groups;
  });

  /* ── 3. Render the initial form ───────────────────────────────── */
  function renderForm(prefill = {}) {
    const classOptions = Object.keys(classMap)
      .map(c => `<option value="${c}" ${prefill.sec === c ? 'selected' : ''}>XII - ${c}</option>`)
      .join('');

    document.getElementById('form').innerHTML = `
      <div id="content-header">
        HSE(+2) EXAMINATION MARCH 2026<br>STUDENT DETAILS FORM
      </div>
      <div class="warning-bar">
        <span>WARNING:</span> Fill the form carefully. Details cannot be changed after final submission.
      </div>
      <div class="form-container">
        <form id="student-form" novalidate>
          <div id="box-header">STUDENT DETAILS</div>
          <hr>

          <div class="input-box">
            <input type="text" name="name" id="name" required placeholder=" "
                   value="${prefill.name || ''}" />
            <label for="name">Name</label>
          </div>

          <table><tbody><tr>
            <td>
              <div class="input-box">
                <input type="text" name="reg_no" id="regno" required placeholder=" "
                       value="${prefill.reg_no || ''}" />
                <label for="regno" style="font-size:13px;">HSC Register Number</label>
              </div>
            </td>
            <td style="width:50%;">
              <div class="input-box">
                <input type="date" name="dob" id="dob" required placeholder=" "
                       value="${prefill.dob || ''}" />
                <label for="dob">Select DOB</label>
              </div>
            </td>
          </tr></tbody></table>

          <div class="input-box">
            <div class="field-wrap">
              <select name="sec" id="sec-select" required>
                <option value="" disabled ${!prefill.sec ? 'selected' : ''} hidden></option>
                ${classOptions}
              </select>
              <label>Select Class</label>
            </div>
          </div>

          <div id="group-section" style="display:none;">
            <div class="input-box radio-input-box">
              <label class="radio-group-label">Select Group</label>
              <div id="group-radios"></div>
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

    /* Attach class-change listener */
    document.getElementById('sec-select').addEventListener('change', function () {
      populateGroups(this.value, prefill.grp || '');
    });

    /* If editing with a prefilled class, show groups immediately */
    if (prefill.sec) populateGroups(prefill.sec, prefill.grp || '');

    document.getElementById('student-form').addEventListener('submit', handleFormSubmit);
  }

  /* ── 4. Populate group radios dynamically ─────────────────────── */
  function populateGroups(classCode, selectedGrp) {
    const groups  = classMap[classCode] || [];
    const section = document.getElementById('group-section');
    const wrap    = document.getElementById('group-radios');

    if (!groups.length) { section.style.display = 'none'; return; }

    const autoSelect = groups.length === 1;   // pre-select if only one option

    wrap.innerHTML = groups.map((g) => {
      const checked = autoSelect || g === selectedGrp ? 'checked' : '';
      return `
        <label class="radio-option">
          <input type="radio" name="grp" value="${g}" ${checked} />
          <span class="radio-custom"></span>
          <span class="radio-text">${GROUP_NAMES[g] || g}</span>
        </label>`;
    }).join('');

    section.style.display = 'block';
  }

  /* ── 5. Collect & validate form values ────────────────────────── */
  function collectForm() {
    const f      = document.getElementById('student-form');
    const name   = f.querySelector('#name').value.trim();
    const reg_no = f.querySelector('#regno').value.trim();
    const dob    = f.querySelector('#dob').value;
    const sec    = f.querySelector('#sec-select').value;
    const grpEl  = f.querySelector('input[name="grp"]:checked');
    const grp    = grpEl ? grpEl.value : '';
    return { name, reg_no, dob, sec, grp };
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

  /* ── 6. Handle form submit → show preview ─────────────────────── */
  function handleFormSubmit(e) {
    e.preventDefault();
    hideError();

    const data = collectForm();

    if (!data.name)   return showError('⚠️ Please enter your name.');
    if (!data.reg_no) return showError('⚠️ Please enter your register number.');
    if (!data.dob)    return showError('⚠️ Please select your date of birth.');
    if (!data.sec)    return showError('⚠️ Please select your class.');
    if (!data.grp)    return showError('⚠️ Please select your group.');

    renderPreview(data);
  }

  /* ── 7. Render preview screen ─────────────────────────────────── */
  function renderPreview(data) {
    const dobFormatted = data.dob
      ? new Date(data.dob).toLocaleDateString('en-IN', { day:'2-digit', month:'long', year:'numeric' })
      : '—';

    document.getElementById('form').innerHTML = `
      <div id="content-header">
        HSE(+2) EXAMINATION MARCH 2026<br>STUDENT DETAILS FORM
      </div>
      <div class="form-container">
        <div id="box-header">📋 Preview — Verify Your Details</div>
        <hr>

        <table class="preview-table">
          <tbody>
            <tr><th>Name</th><td>${escHtml(data.name)}</td></tr>
            <tr><th>Register No.</th><td>${escHtml(data.reg_no)}</td></tr>
            <tr><th>Date of Birth</th><td>${dobFormatted}</td></tr>
            <tr><th>Class</th><td>XII - ${escHtml(data.sec)}</td></tr>
            <tr><th>Group</th><td>${escHtml(GROUP_NAMES[data.grp] || data.grp)}</td></tr>
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

  /* ── 8. POST to Flask ─────────────────────────────────────────── */
  async function submitToBackend(data) {
    const overlay = createLoadingOverlay();
    document.getElementById('form').appendChild(overlay);

    const formData = new FormData();
    Object.entries(data).forEach(([k, v]) => formData.append(k, v));

    try {
      const response = await fetch('/HSC/form/submit', {
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

  /* ── 9. Success screen ────────────────────────────────────────── */
  function renderSuccess(result, data) {
    document.getElementById('form').innerHTML = `
      <div id="content-header">
        HSE(+2) EXAMINATION MARCH 2026<br>STUDENT DETAILS FORM
      </div>
      <div class="form-container">
        <div id="box-header">✅ Submitted Successfully</div>
        <hr>
        <div style="text-align:center;padding:28px 16px;line-height:2;">
          <div style='font-size: 17px;'>Your details have been recorded successfully.</div>
          <strong>${escHtml(result.name || data.name)}</strong><br>
          <span style="color:#555;">Register No: ${escHtml(result.reg_no || data.reg_no)}</span>
        </div>
      </div>`;
  }

  /* ── 10. Helpers ──────────────────────────────────────────────── */
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

  /* ── 11. Inject required CSS ──────────────────────────────────── */
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

    /* ── Radio group box ── */
    .radio-input-box {
      border: 1.5px solid #ccc;
      border-radius: 10px;
      padding: 10px 16px 12px;
      position: relative;
      transition: border-color 0.22s, box-shadow 0.22s;
    }
    .radio-input-box:focus-within {
      border-color: #534AB7;
      box-shadow: 0 0 0 3.5px rgba(83,74,183,0.13);
    }
    .radio-group-label {
      display: block;
      font-size: 11.5px;
      font-weight: 500;
      color: #534AB7;
      margin-bottom: 8px;
    }

    /* ── Radio options ── */
    .radio-option {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 6px 4px;
      cursor: pointer;
      font-size: 14px;
      color: #333;
      user-select: none;
    }
    .radio-option input[type="radio"] {
      display: none;
    }
    .radio-custom {
      width: 18px; height: 18px;
      border: 2px solid #ccc;
      border-radius: 50%;
      flex-shrink: 0;
      position: relative;
      transition: border-color 0.2s;
      background: #fff;
    }
    .radio-custom::after {
      content: '';
      position: absolute;
      top: 50%; left: 50%;
      transform: translate(-50%, -50%) scale(0);
      width: 8px; height: 8px;
      border-radius: 50%;
      background: #534AB7;
      transition: transform 0.18s ease;
    }
    .radio-option input[type="radio"]:checked ~ .radio-custom {
      border-color: #534AB7;
    }
    .radio-option input[type="radio"]:checked ~ .radio-custom::after {
      transform: translate(-50%, -50%) scale(1);
    }
    .radio-option:hover .radio-custom {
      border-color: #534AB7;
    }
    .radio-text {
      line-height: 1.3;
    }

    #group-radios label.radio-option,
    .radio-input-box > label.radio-group-label {
      position: static;
      top: auto;
      left: auto;
      transform: none;
      background: transparent;
      pointer-events: auto;
    }
    #group-radios label.radio-option { padding: 6px 4px; }
    .radio-input-box > label.radio-group-label { padding: 0; }
  `;
  document.head.appendChild(style);

  /* ── 12. Kick off ─────────────────────────────────────────────── */
  renderForm();

})();