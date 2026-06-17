let clsnos = document.getElementById('cls_nos');

function buildGroupSection(clsIdx, count) {
    let html = '<div style="display:flex;flex-direction:column;gap:6px;">';
    for (let g = 1; g <= count; g++) {
        html += `<div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:11px;font-weight:600;min-width:52px;">Group ${g}</span>
            <input list="group-options" name="cls${clsIdx}_grp${g}"
                placeholder="Select or type group..."
                style="flex:1;padding:5px 8px;border:1px solid #9aa5b0;border-radius:6px;font-size:12px;outline:none;" />
        </div>`;
    }
    html += '</div>';
    return html;
}

function onGroupCountChange(inp, clsIdx) {
    const val = parseInt(inp.value);
    const cell = document.getElementById('grp_detail_' + clsIdx);
    cell.innerHTML = (val >= 1) ? buildGroupSection(clsIdx, val) : '';
}

function buildRows(count) {
    const tbody = document.getElementById('cls_tbody');
    const submitWrap = document.getElementById('submit_wrap');
    tbody.innerHTML = '';
    if (!count || count < 1) {
        submitWrap.style.display = 'none';
        return;
    }
    for (let i = 1; i <= count; i++) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                XII - <input type="text" name="cls${i}_section" placeholder="e.g. A" maxlength="5"
                    style="width:40%;padding:5px 8px;border:1px solid #9aa5b0;border-radius:6px;
                           font-size:13px;font-weight:600;text-align:center;background:#f4f6f8;outline:none;" />
            </td>
            <td>
                <input type="number" min="1" max="10" placeholder="e.g. 2"
                    style="width:64px;padding:5px;border:1px solid #9aa5b0;border-radius:6px;font-size:12px;text-align:center;"
                    oninput="onGroupCountChange(this, ${i})" />
            </td>
            <td id="grp_detail_${i}" style="font-weight:normal;"></td>
        `;
        tbody.appendChild(tr);
    }
    submitWrap.style.display = 'flex';
}

clsnos.addEventListener('input', function () {
    buildRows(parseInt(this.value) || 0);
});

function showMessage(success, message) {
    let existing = document.getElementById('submit_msg');
    if (existing) existing.remove();

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
    document.getElementById('submit_wrap').insertAdjacentElement('afterend', div);
}

function validateData(rows) {
    for (let i = 0; i < rows.length; i++) {
        const section = rows[i].section.trim();
        if (!section) return `Class ${i + 1}: Section name is empty.`;
        if (rows[i].groups.length === 0) return `Class ${i + 1} (${section}): No. of groups not entered.`;
        for (let g = 0; g < rows[i].groups.length; g++) {
            if (!rows[i].groups[g].trim()) return `Class ${i + 1} (${section}): Group ${g + 1} is empty.`;
        }
    }
    return null;
}

async function handleSubmit() {
    const rows = document.querySelectorAll('#cls_tbody tr');
    const result = [];

    rows.forEach((tr, idx) => {
        const section = tr.querySelector('input[type="text"]')?.value || '';
        const groups = [...tr.querySelectorAll('input[list="group-options"]')].map(inp => inp.value.trim());
        result.push({ class: idx + 1, section: section.trim(), groups });
    });

    // Validate before sending
    const error = validateData(result);
    if (error) {
        showMessage(false, '⚠ ' + error);
        return;
    }

    const btn = document.querySelector('.submit-wrap button');
    btn.disabled = true;
    btn.textContent = 'Submitting...';

    try {
        const response = await fetch('http://localhost:8000/hsc-class-details', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ classes: result })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(true, '✓ ' + (data.message || 'Data submitted successfully!'));
        } else {
            showMessage(false, '✗ ' + (data.detail || 'Submission failed. Please try again.'));
        }
    } catch (err) {
        showMessage(false, '✗ Could not reach the server. Please check your connection.');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Final Submit';
    }
}

if (response.ok) {
    showMessage(true, '✓ ' + (data.message || 'Data submitted successfully!'));

    let seconds = 5;
    const countEl = document.createElement('div');
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