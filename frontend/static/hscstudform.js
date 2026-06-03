form=`<div id="content-header">HSE(+2) EXAMINATION MARCH 2026 <br> STUDENT DETAILS FORM</div>
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
                    <label for="regno">HSC Register Number</label>
                </div>
                <div class="input-box">
                    <input type="date" name='dob' id="dob" required placeholder=" " />
                    <label for="dob">Select DOB</label>
                </div>
                <div class="input-box">
                    <div class="field-wrap">
                        <select name='sec' required>
                            <option value="" disabled selected hidden></option>
                            <option value="A1">XII - A1</option>
                            <option value="A">XII - A</option>
                            <option value="B">XII - B</option>
                            <option value="C">XII - C</option>
                            <option value="D">XII - D</option>
                            <option value="E">XII - E</option>
                            <option value="F">XII - F</option>
                            <option value="G1">XII - G1</option>
                            <option value="G2">XII - G2</option>
                        </select>
                        <label>Select Class</label>
                    </div>
                </div>
                <div class="input-box">
                    <div class="field-wrap">
                        <select name='grp' required>
                            <option value="" disabled selected hidden></option>
                            <option value="csc">COMPUTER SCIENCE/MATHS</option>
                            <option value="biomat">BIOLOGY/MATHS</option>
                            <option value="biocs">BIOLOGY/COMPUTER SCIENCE</option>
                            <option value="artsca">ARTS/COMPUTER APPLICATION</option>
                            <option value="artsbm">ARTS/BUSINESS MATHS</option>
                            <option value="bme">BASIC MECHANICAL ENGINEERING/MATHS</option>
                        </select>
                        <label>Select Group</label>
                    </div>
                </div>
                <div class="btn">
                    <button type="submit" id="login-btn">SUBMIT</button>
                </div>
            </form>
        </div>`
document.getElementById('form').innerHTML=form;