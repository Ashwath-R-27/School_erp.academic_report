form = `<div id="content-header">SSLC EXAMINATION MARCH 2026 <br> STUDENT DETAILS FORM</div>
        <div class="form-container">
            <form id="student-form">
                <div id="box-header">STUDENT DETAILS</div>
                <hr>
                <div class="input-box">
                    <input type="text" name='name' id="name" required placeholder=" " />
                    <label for="name">Name</label>
                </div>
                <div class="input-box">
                    <input type="text" name='reg_no' id="regno" required placeholder=" " />
                    <label for="regno">SSLC Register Number</label>
                </div>
                <div class="input-box">
                    <input type="date" name='dob' id="dob" required placeholder=" " />
                    <label for="dob">Select DOB</label>
                </div>
                <div class="input-box">
                    <div class="field-wrap">
                        <select name='sec' required>
                            <option value="" disabled selected hidden></option>
                            <option value="A">X - A</option>
                            <option value="B">X - B</option>
                            <option value="C">X - C</option>
                            <option value="D">X - D</option>
                            <option value="E">X - E</option>
                        </select>
                        <label>Select Class</label>
                    </div>
                </div>
                <div id="error-msg" style="display:none; color:red; text-align:center; padding: 8px; margin: 8px 0; border: 1px solid red; border-radius: 4px; font-size: 0.9em;"></div>
                <div class="btn">
                    <button type="submit" id="login-btn">SUBMIT</button>
                </div>
            </form>
        </div>`;

document.getElementById('form').innerHTML = form;

document.getElementById('student-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const submitBtn = document.getElementById('login-btn');
    const errorMsg = document.getElementById('error-msg');

    errorMsg.style.display = 'none';
    errorMsg.textContent = '';
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';

    try {
        const response = await fetch('/submit/sslc', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            document.getElementById('form').innerHTML = `
                <div id="content-header">SSLC EXAMINATION MARCH 2026 <br> STUDENT DETAILS FORM</div>
                <div class="form-container">
                    <div id="box-header">✅ Submitted Successfully</div>
                    <hr>
                    <p style="text-align:center; padding: 20px;">
                        Your details have been recorded.<br><br>
                        <strong>${result.name}</strong><br>
                        Register No: ${result.reg_no}
                    </p>
                </div>`;
        } else {
            const isDuplicate = result.detail && result.detail.includes('already exists');
            errorMsg.textContent = isDuplicate
                ? '⚠️ This Register Number has already been submitted.'
                : (result.detail || 'Submission failed. Please try again.');
            errorMsg.style.display = 'block';
            submitBtn.disabled = false;
            submitBtn.textContent = 'SUBMIT';
        }
    } catch (err) {
        errorMsg.textContent = 'Network error. Please check your connection.';
        errorMsg.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.textContent = 'SUBMIT';
    }
});