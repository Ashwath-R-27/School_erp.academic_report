// ── Eye toggles ──────────────────────────────────────────────────────
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

// ── Global declarations ───────────────────────────────────────────────
const emailRegex   = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const sendOtpBtn   = document.getElementById('send-otp-btn');
const verifyOtpBtn = document.getElementById('verify-otp-btn');
const cancelOtpBtn = document.getElementById('cancel-otp-btn');
const resendBtn    = document.getElementById('resend-btn');
const overlay      = document.getElementById('otp-overlay');
const registerBtn  = document.getElementById('login-btn');

// Disable both buttons by default
sendOtpBtn.disabled = true;
sendOtpBtn.style.opacity = '0.4';
sendOtpBtn.style.cursor = 'not-allowed';

registerBtn.disabled = true;
registerBtn.style.opacity = '0.4';
registerBtn.style.cursor = 'not-allowed';

// ── Live validation ───────────────────────────────────────────────────
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
        showSuccess('conpwd', 'Passwords matched ✓');
}

document.getElementById('em').addEventListener('input', function () {
    if (!emailRegex.test(this.value.trim())) {
        showError('em', 'Enter a valid email address.');
        sendOtpBtn.disabled = true;
        sendOtpBtn.style.opacity = '0.4';
        sendOtpBtn.style.cursor = 'not-allowed';
    } else {
        clearMsg('em');
        sendOtpBtn.disabled = false;
        sendOtpBtn.style.opacity = '1';
        sendOtpBtn.style.cursor = 'pointer';
    }
});

// ── Submit guard ──────────────────────────────────────────────────────
document.querySelector('form').addEventListener('submit', function (e) {
    const name   = document.getElementById('name').value.trim();
    const un     = document.getElementById('un').value.trim();
    const pwd    = document.getElementById('pwd').value;
    const conpwd = document.getElementById('conpwd').value;
    const em     = document.getElementById('em').value.trim();
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

// ── OTP Logic ─────────────────────────────────────────────────────────
let otpTimer = null;

function startOtpTimer() {
    let seconds = 120;
    resendBtn.disabled = true;
    resendBtn.style.opacity = '0.4';

    clearInterval(otpTimer);
    otpTimer = setInterval(() => {
        seconds--;
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        document.getElementById('otp-timer').textContent =
            `${m}:${s.toString().padStart(2, '0')}`;

        if (seconds <= 0) {
            clearInterval(otpTimer);
            resendBtn.disabled = false;
            resendBtn.style.opacity = '1';
            document.getElementById('otp-timer').textContent = '0:00';
        }
    }, 1000);
}

async function sendOtp() {
    const email = document.getElementById('em').value.trim();
    try {
        const res = await fetch('/send-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await res.json();

        if (res.ok) {
            document.getElementById('otp-email-display').textContent = email;
            document.getElementById('otp-error').textContent = '';
            document.getElementById('otp-input').value = '';
            overlay.style.display = 'flex';
            startOtpTimer();
        } else {
            showError('em', data.detail || 'Failed to send OTP.');
        }
    } catch {
        showError('em', 'Server error. Try again.');
    }
}

sendOtpBtn.addEventListener('click', sendOtp);

resendBtn.addEventListener('click', async () => {
    const email = document.getElementById('em').value.trim();
    try {
        await fetch('/send-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        document.getElementById('otp-input').value = '';
        document.getElementById('otp-error').textContent = '';
        startOtpTimer();
    } catch {
        document.getElementById('otp-error').textContent = 'Failed to resend. Try again.';
    }
});

verifyOtpBtn.addEventListener('click', async () => {
    const email = document.getElementById('em').value.trim();
    const otp   = document.getElementById('otp-input').value.trim();

    if (otp.length !== 6) {
        document.getElementById('otp-error').textContent = 'Enter a valid 6-digit OTP.';
        return;
    }

    try {
        const res = await fetch('/verify-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, otp })
        });
        const data = await res.json();

        if (res.ok && data.verified) {
            clearInterval(otpTimer);
            overlay.style.display = 'none';
            registerBtn.disabled = false;
            registerBtn.style.opacity = '1';
            registerBtn.style.cursor = 'pointer';
            showSuccess('em', 'Email verified ✓');
        } else {
            document.getElementById('otp-error').textContent = data.detail || 'Incorrect OTP.';
        }
    } catch {
        document.getElementById('otp-error').textContent = 'Server error. Try again.';
    }
});

cancelOtpBtn.addEventListener('click', () => {
    clearInterval(otpTimer);
    overlay.style.display = 'none';
});