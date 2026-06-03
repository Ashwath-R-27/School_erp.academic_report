form=`<div id="content-header">SSLC EXAMINATION MARCH 2026 <br> STUDENT DETAILS FORM</div>
        <div class="form-container">
            <form action="" method="post">
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
                <div class="btn">
                    <button type="submit" id="login-btn">SUBMIT</button>
                </div>
            </form>
        </div>`
document.getElementById('form').innerHTML=form;