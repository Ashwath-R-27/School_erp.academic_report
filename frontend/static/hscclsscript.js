// The 3 groups offered as checkboxes for every class.
// Value is what gets sent to the backend; label is what the user sees.
const GROUPS = [
    { label: 'Computer Science / Maths', value: 'csc' },
    { label: 'Biology / Maths', value: 'biomat' },
    { label: 'Biology / Computer Science', value: 'biocs' },
    { label: 'Arts / Computer Application', value: 'artsca' },
    { label: 'Arts / Business Maths', value: 'artsbm' },
    { label: 'Basic Mechanical Engineering / Maths', value: 'bme' }
];

let rowCounter = 0;

function buildGroupChecks(rowId) {
    return GROUPS.map(g => `
        <label class="group-check-item">
            <input type="checkbox" data-row="${rowId}" value="${g.value}" />
            ${g.label}
        </label>
    `).join('');
}

function addRow() {
    rowCounter++;
    const rowId = rowCounter;
    const tbody = document.getElementById('cls_tbody');

    const tr = document.createElement('tr');
    tr.dataset.rowId = rowId;
    tr.innerHTML = `
        <td>
            XII - <input type="text" data-role="section" class="section-input" placeholder="e.g. A" maxlength="5" />
        </td>
        <td>
            <div class="group-checks">${buildGroupChecks(rowId)}</div>
        </td>
        <td>
            <button type="button" class="remove-row-btn" onclick="removeRow(this)">Remove</button>
        </td>
    `;
    tbody.appendChild(tr);
}

function removeRow(btn) {
    const tbody = document.getElementById('cls_tbody');
    if (tbody.children.length <= 1) {
        showMessage(false, '⚠ At least one class row is required.', document.getElementById('submit_wrap'));
        return;
    }
    btn.closest('tr').remove();
}

function collectData() {
    const rows = document.querySelectorAll('#cls_tbody tr');
    const result = [];
    rows.forEach(tr => {
        const section = tr.querySelector('input[data-role="section"]').value.trim();
        const checked = [...tr.querySelectorAll('input[type="checkbox"]:checked')].map(c => c.value);
        result.push({ class: section, groups: checked });
    });
    return result;
}

function validateData(rows) {
    const seen = new Set();
    for (let i = 0; i < rows.length; i++) {
        const section = rows[i].class;
        if (!section) return `Class ${i + 1}: Section name is empty.`;

        const key = section.toUpperCase();
        if (seen.has(key)) return `Section "${section}" has been entered more than once.`;
        seen.add(key);

        if (rows[i].groups.length === 0) return `Class ${section}: Select at least one group.`;
    }
    return null;
}

function groupLabel(value) {
    const found = GROUPS.find(g => g.value === value);
    return found ? found.label : value;
}

function showMessage(success, message, anchorEl) {
    let existing = document.getElementById('submit_msg');
    if (existing) existing.remove();
    let existingTimer = document.getElementById('redirect_timer');
    if (existingTimer) existingTimer.remove();

    const div = document.createElement('div');
    div.id = 'submit_msg';
    div.textContent = message;
    div.style.cssText = `
        margin-top: 14px;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        text-align: center;
        background-color: ${success ? '#e6f4ea' : '#fdecea'};
        color: ${success ? '#2e7d32' : '#c0392b'};
        border: 1px solid ${success ? '#a8d5b0' : '#f5c6c6'};
    `;
    anchorEl.insertAdjacentElement('afterend', div);
}

function handleSubmit() {
    const data = collectData();
    const error = validateData(data);
    if (error) {
        showMessage(false, '⚠ ' + error, document.getElementById('submit_wrap'));
        return;
    }

    const existingMsg = document.getElementById('submit_msg');
    if (existingMsg) existingMsg.remove();

    const previewTbody = document.getElementById('preview_tbody');
    previewTbody.innerHTML = data.map(row => `
        <tr>
            <td>XII - ${row.class}</td>
            <td>${row.groups.map(groupLabel).join(', ')}</td>
        </tr>
    `).join('');

    document.getElementById('cls_dtls').style.display = 'none';
    document.getElementById('add_row_wrap').style.display = 'none';
    document.getElementById('submit_wrap').style.display = 'none';
    document.getElementById('preview_section').style.display = 'flex';
}

function handleEdit() {
    document.getElementById('preview_section').style.display = 'none';
    document.getElementById('cls_dtls').style.display = 'block';
    document.getElementById('add_row_wrap').style.display = 'flex';
    document.getElementById('submit_wrap').style.display = 'flex';
}

async function handleFinalSubmit() {
    const data = collectData();
    const error = validateData(data);
    if (error) {
        handleEdit();
        showMessage(false, '⚠ ' + error, document.getElementById('submit_wrap'));
        return;
    }

    const finalBtn = document.querySelector('.preview-actions .btn-primary');
    const editBtn = document.querySelector('.preview-actions .btn-secondary');
    finalBtn.disabled = true;
    editBtn.disabled = true;
    finalBtn.textContent = 'Submitting...';

    try {
        const response = await fetch('/hsc-class-details/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const responseData = await response.json();

        if (response.ok) {
            document.querySelector('.preview-actions').style.display = 'none';
            showMessage(true, '✓ ' + (responseData.message || 'Data submitted successfully!'), document.getElementById('preview_table_wrap'));
            startRedirectCountdown();
        } else {
            showMessage(false, '✗ ' + (responseData.detail || 'Submission failed. Please try again.'), document.querySelector('.preview-actions'));
            finalBtn.disabled = false;
            editBtn.disabled = false;
            finalBtn.textContent = 'Final Submit';
        }
    } catch (err) {
        showMessage(false, '✗ Could not reach the server. Please check your connection.', document.querySelector('.preview-actions'));
        finalBtn.disabled = false;
        editBtn.disabled = false;
        finalBtn.textContent = 'Final Submit';
    }
}

function startRedirectCountdown() {
    let seconds = 5;
    const countEl = document.createElement('div');
    countEl.id = 'redirect_timer';
    countEl.style.cssText = `
        margin-top: 8px;
        font-size: 13px;
        color: #555;
        text-align: center;
    `;
    countEl.textContent = `Redirecting to dashboard in ${seconds}s...`;
    document.getElementById('submit_msg').insertAdjacentElement('afterend', countEl);

    const timer = setInterval(() => {
        seconds--;
        if (seconds <= 0) {
            clearInterval(timer);
            window.location.href = '/dashboard';
        } else {
            countEl.textContent = `Redirecting to dashboard in ${seconds}s...`;
        }
    }, 1000);
}

document.addEventListener('DOMContentLoaded', () => {
    addRow();
});