
    // ── Eye toggles (fixed — unique IDs per field) ──────────────────────
    function setupEye(inputId, btnId, iconId) {
        const input = document.getElementById(inputId);
        const btn   = document.getElementById(btnId);
        const icon  = document.getElementById(iconId);
        btn.addEventListener('click', () => {
            const hide = input.type === 'password';
            input.type = hide ? 'text' : 'password';
            icon.className = hide ? 'ti ti-eye-off' : 'ti ti-eye';
            btn.setAttribute('aria-label', hide ? 'Hide password' : 'Show password');
            input.focus();
        });
    }
    setupEye('pwd',    'eye-btn-1', 'eye-icon-1');
    setupEye('conpwd', 'eye-btn-2', 'eye-icon-2');

    // ── Helpers ──────────────────────────────────────────────────────────
    function showError(fieldId, msg) {
        const el = document.getElementById('err-' + fieldId);
        el.textContent = msg;
        el.style.color = 'red';
        el.style.display = 'block';
    }
    function showSuccess(fieldId, msg) {
        const el = document.getElementById('err-' + fieldId);
        el.textContent = msg;
        el.style.color = 'green';
        el.style.display = 'block';
    }
    function clearMsg(fieldId) {
        const el = document.getElementById('err-' + fieldId);
        el.textContent = '';
        el.style.display = 'none';
    }

    // ── Live validation ──────────────────────────────────────────────────
    document.getElementById('name').addEventListener('input', function () {
        if (this.value.trim().length < 3)
            showError('name', 'Full name must be at least 3 characters.');
        else clearMsg('name');
    });

    document.getElementById('un').addEventListener('input', function () {
        if (this.value.trim().length < 3)
            showError('un', 'Username must be at least 3 characters.');
        else if (/\s/.test(this.value))
            showError('un', 'Username cannot contain spaces.');
        else clearMsg('un');
    });

    document.getElementById('pwd').addEventListener('input', function () {
        const v = this.value;
        if (v.length < 8)
            showError('pwd', 'Password must be at least 8 characters.');
        else if (!/[A-Z]/.test(v))
            showError('pwd', 'Password must have at least one uppercase letter.');
        else if (!/[0-9]/.test(v))
            showError('pwd', 'Password must have at least one number.');
        else
            clearMsg('pwd');

        // re-check confirm field live
        checkConfirm();
    });

    document.getElementById('conpwd').addEventListener('input', checkConfirm);

    function checkConfirm() {
        const pwd    = document.getElementById('pwd').value;
        const conpwd = document.getElementById('conpwd').value;
        if (!conpwd) { clearMsg('conpwd'); return; }
        if (pwd !== conpwd)
            showError('conpwd', 'Passwords do not match.');
        else
            showSuccess('conpwd', 'Password matched ✓');
    }

    document.getElementById('em').addEventListener('input', function () {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(this.value))
            showError('em', 'Enter a valid email address.');
        else clearMsg('em');
    });

    // ── Submit guard ─────────────────────────────────────────────────────
    document.querySelector('form').addEventListener('submit', function (e) {
        const name   = document.getElementById('name').value.trim();
        const un     = document.getElementById('un').value.trim();
        const pwd    = document.getElementById('pwd').value;
        const conpwd = document.getElementById('conpwd').value;
        const em     = document.getElementById('em').value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        let valid = true;

        if (name.length < 3)          { showError('name',   'Full name must be at least 3 characters.'); valid = false; }
        if (un.length < 3)            { showError('un',     'Username must be at least 3 characters.'); valid = false; }
        if (pwd.length < 8)           { showError('pwd',    'Password must be at least 8 characters.'); valid = false; }
        else if (!/[A-Z]/.test(pwd))  { showError('pwd',    'Password must have at least one uppercase letter.'); valid = false; }
        else if (!/[0-9]/.test(pwd))  { showError('pwd',    'Password must have at least one number.'); valid = false; }
        if (pwd !== conpwd)           { showError('conpwd', 'Passwords do not match.'); valid = false; }
        if (!emailRegex.test(em))     { showError('em',     'Enter a valid email address.'); valid = false; }

        if (!valid) e.preventDefault();
    });
