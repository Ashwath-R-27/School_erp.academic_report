from flask import Flask, render_template, request , url_for, redirect

app = Flask(__name__)



def header_div():
    logo_url=url_for('static', filename='logo.png')
    header=f""" <div class="header">
        <div class="logo"><a href="#"><img src="{logo_url}" id="logo"></a></div>
        <div class="header_content">
            <div class="header_text_1">SVGV MATRICULATION HIGHER SECONDARY SCHOOL</div>
        </div>
    </div>"""
    return header

def hscgroups():
    grpdtls=[{'name':'COMPUTER SCIENCE + MATHS','code':'csc','sub1':'PHY','sub2':'CHEM','sub3':'COMP','sub4':'MATHS'},{'name':'BIOLOGY + MATHS','code':'biomat','sub1':'PHY','sub2':'CHEM','sub3':'BIO','sub4':'MATHS'}]
    return grpdtls

def hsc_records():
    datas=[{'rank': 1, 'reg_no': 3265566, 'class': 'A1', 'group': 'csc', 'name': 'JEEVIKA G', 'lang': 99, 'eng': 95, 'sub1': 98, 'sub2': 97, 'sub3': 91, 'sub4': 99, 'total': 579, 'cutoff': 196.5}, {'rank': 2, 'reg_no': 3265552, 'class': 'A', 'group': 'biomat', 'name': 'AMUTHAVAANI K', 'lang': 97, 'eng': 98, 'sub1': 88, 'sub2': 95, 'sub3': 96, 'sub4': 95, 'total': 569, 'cutoff': 186.5}, {'rank': 3, 'reg_no': 3265606, 'class': 'A', 'group': 'csc', 'name': 'RASHEETH N', 'lang': 96, 'eng': 97, 'sub1': 87, 'sub2': 96, 'sub3': 95, 'sub4': 97, 'total': 568, 'cutoff': 188.5}, {'rank': 4, 'reg_no': 3265580, 'class': 'A1', 'group': 'biomat', 'name': 'RITHANYA S', 'lang': 97, 'eng': 99, 'sub1': 90, 'sub2': 96, 'sub3': 91, 'sub4': 94, 'total': 567, 'cutoff': 187.0}, {'rank': 5, 'reg_no': 3265594, 'class': 'A1', 'group': 'biomat', 'name': 'DARSHAN G', 'lang': 96, 'eng': 98, 'sub1': 86, 'sub2': 94, 'sub3': 94, 'sub4': 94, 'total': 562, 'cutoff': 184.0}, {'rank': 6, 'reg_no': 3265565, 'class': 'A1', 'group': 'biomat', 'name': 'HARSHITHA S G', 'lang': 99, 'eng': 97, 'sub1': 85, 'sub2': 92, 'sub3': 98, 'sub4': 90, 'total': 561, 'cutoff': 178.5}, {'rank': 7, 'reg_no': 3265572, 'class': 'A1', 'group': 'biomat', 'name': 'MRITHIKA S', 'lang': 97, 'eng': 96, 'sub1': 90, 'sub2': 89, 'sub3': 86, 'sub4': 97, 'total': 555, 'cutoff': 186.5}, {'rank': 8, 'reg_no': 3265591, 'class': 'A1', 'group': 'biomat', 'name': 'VAISHNAVI K R', 'lang': 97, 'eng': 98, 'sub1': 83, 'sub2': 85, 'sub3': 90, 'sub4': 93, 'total': 546, 'cutoff': 177.0}, {'rank': 9, 'reg_no': 3265583, 'class': 'A1', 'group': 'biomat', 'name': 'SANJITHA V M', 'lang': 94, 'eng': 93, 'sub1': 81, 'sub2': 82, 'sub3': 83, 'sub4': 79, 'total': 512, 'cutoff': 160.5}]
    return datas

@app.route("/")
def first():
    return redirect (url_for('loginpg'))

@app.route("/login")
def loginpg():
    header=header_div()
    return render_template("login.html",header_div=header)

@app.route("/register")
def registerpg():
    header=header_div()
    return render_template("register.html",header_div=header)

@app.route("/home")
def home():
    header=header_div()
    return render_template("home.html",header_div=header)



@app.route("/HSC_2026")
def hscmark():
    header=header_div()
    return render_template("hscmarkpg.html",header_div=header)

@app.route("/SSLC_2026")
def sslcmark():
    header=header_div()
    return render_template("sslcmarkpg.html",header_div=header)

@app.route("/HSC_2026/Marks/Group")
def hscgrpwisemarks():
    datas=hsc_records()
    header=header_div()
    groups=hscgroups()
    return render_template("hscgrpmark.html",header_div=header,records=datas,groups=groups,length=len(groups),len2=len(datas))

@app.route("/HSC_2026/Marks/Class")
def hscclasswisemarks():
    cls=[{'sec':'A1','grp':[{'name':'COMPUTER SCIENCE + MATHS','code':'csc','sub1':'PHY','sub2':'CHEM','sub3':'COMP','sub4':'MATHS'},{'name':'BIOLOGY + MATHS','code':'biomat','sub1':'PHY','sub2':'CHEM','sub3':'BIO','sub4':'MATHS'}]},{'sec':'A','grp':[{'name':'COMPUTER SCIENCE + MATHS','code':'csc','sub1':'PHY','sub2':'CHEM','sub3':'COMP','sub4':'MATHS'},{'name':'BIOLOGY + MATHS','code':'biomat','sub1':'PHY','sub2':'CHEM','sub3':'BIO','sub4':'MATHS'}]}]
    datas=hsc_records()
    header=header_div()
    return render_template("hscclsmarkpg.html",header_div=header,records=datas,cls=cls,length=len(cls),len1=len(cls[0]['grp']),len2=len(datas))

@app.route("/SSLC_2026/Marks")
def sslcclassmark():
    header=header_div()
    cls=['A','B','C','D','E']
    datas=[{'rank': 1, 'reg_no': 5287481, 'class': 'E', 'name': 'ASHWATH R', 'tamil': 99, 'english': 99, 'maths': 100, 'science': 100, 'social': 100, 'total': 493}, {'rank': 1, 'reg_no': 5367867, 'class': 'B', 'name': 'NILAKSHA R', 'tamil': 97, 'english': 99, 'maths': 100, 'science': 99, 'social': 98, 'total': 493}, {'rank': 1, 'reg_no': 5367958, 'class': 'E', 'name': 'NAVADEEP S J', 'tamil': 97, 'english': 99, 'maths': 98, 'science': 99, 'social': 100, 'total': 493}, {'rank': 2, 'reg_no': 5367946, 'class': 'D', 'name': 'KISHORE M', 'tamil': 95, 'english': 99, 'maths': 99, 'science': 99, 'social': 100, 'total': 492}, {'rank': 3, 'reg_no': 5367939, 'class': 'D', 'name': 'ISHAC HANIF N', 'tamil': 96, 'english': 98, 'maths': 98, 'science': 99, 'social': 100, 'total': 491}, {'rank': 4, 'reg_no': 5367902, 'class': 'D', 'name': 'YASHINI V', 'tamil': 97, 'english': 98, 'maths': 97, 'science': 99, 'social': 98, 'total': 489}, {'rank': 4, 'reg_no': 5368000, 'class': 'E', 'name': 'YOGITH A', 'tamil': 98, 'english': 99, 'maths': 99, 'science': 99, 'social': 94, 'total': 489}, {'rank': 5, 'reg_no': 5367871, 'class': 'C', 'name': 'PRITHISHA S', 'tamil': 98, 'english': 97, 'maths': 97, 'science': 99, 'social': 97, 'total': 488}, {'rank': 5, 'reg_no': 5367989, 'class': 'E', 'name': 'SURYA R', 'tamil': 96, 'english': 98, 'maths': 98, 'science': 99, 'social': 97, 'total': 488}, {'rank': 6, 'reg_no': 5367858, 'class': 'B', 'name': 'MITHRA N', 'tamil': 96, 'english': 98, 'maths': 94, 'science': 100, 'social': 99, 'total': 487}, {'rank': 6, 'reg_no': 5367956, 'class': 'D', 'name': 'MUGESH BARATHI V G', 'tamil': 93, 'english': 98, 'maths': 99, 'science': 99, 'social': 98, 'total': 487}, {'rank': 7, 'reg_no': 5367838, 'class': 'A', 'name': 'HARSHINI K', 'tamil': 92, 'english': 98, 'maths': 97, 'science': 99, 'social': 100, 'total': 486}, {'rank': 7, 'reg_no': 5367863, 'class': 'B', 'name': 'NEHA D', 'tamil': 97, 'english': 98, 'maths': 96, 'science': 96, 'social': 99, 'total': 486}, {'rank': 7, 'reg_no': 5367877, 'class': 'C', 'name': 'SAMSKRITI B J', 'tamil': 98, 'english': 96, 'maths': 96, 'science': 100, 'social': 96, 'total': 486}, {'rank': 7, 'reg_no': 5367898, 'class': 'D', 'name': 'VAISHNAVI R', 'tamil': 91, 'english': 98, 'maths': 98, 'science': 99, 'social': 100, 'total': 486}, {'rank': 8, 'reg_no': 5367868, 'class': 'C', 'name': 'NITIKSHA V A', 'tamil': 98, 'english': 94, 'maths': 94, 'science': 99, 'social': 100, 'total': 485}, {'rank': 9, 'reg_no': 5367982, 'class': 'E', 'name': 'SHARATH R', 'tamil': 98, 'english': 97, 'maths': 95, 'science': 96, 'social': 98, 'total': 484}, {'rank': 10, 'reg_no': 5367892, 'class': 'D', 'name': 'TEEKSHIHA K', 'tamil': 98, 'english': 98, 'maths': 92, 'science': 95, 'social': 100, 'total': 483}, {'rank': 11, 'reg_no': 5367833, 'class': 'A', 'name': 'DHIYA M R', 'tamil': 93, 'english': 96, 'maths': 95, 'science': 99, 'social': 97, 'total': 480}, {'rank': 11, 'reg_no': 5367999, 'class': 'E', 'name': 'YESWANTH S', 'tamil': 93, 'english': 99, 'maths': 94, 'science': 95, 'social': 99, 'total': 480}, {'rank': 12, 'reg_no': 5367834, 'class': 'A', 'name': 'DIKSHITHA K', 'tamil': 97, 'english': 98, 'maths': 93, 'science': 98, 'social': 93, 'total': 479}, {'rank': 13, 'reg_no': 5367842, 'class': 'A', 'name': 'JAISHREE K', 'tamil': 96, 'english': 91, 'maths': 90, 'science': 99, 'social': 100, 'total': 476}, {'rank': 13, 'reg_no': 5367957, 'class': 'D', 'name': 'NANDABALAN N', 'tamil': 97, 'english': 98, 'maths': 91, 'science': 98, 'social': 92, 'total': 476}, {'rank': 14, 'reg_no': 5367837, 'class': 'A', 'name': 'HARIDHASHRI S', 'tamil': 92, 'english': 97, 'maths': 95, 'science': 97, 'social': 92, 'total': 473}, {'rank': 15, 'reg_no': 5367835, 'class': 'A', 'name': 'DIVYA PRABHA. P', 'tamil': 91, 'english': 95, 'maths': 92, 'science': 99, 'social': 95, 'total': 472}, {'rank': 16, 'reg_no': 5367884, 'class': 'C', 'name': 'SRIVIDHYA S', 'tamil': 93, 'english': 90, 'maths': 95, 'science': 97, 'social': 96, 'total': 471}, {'rank': 17, 'reg_no': 5367925, 'class': 'D', 'name': 'DIKSHITH S', 'tamil': 87, 'english': 96, 'maths': 92, 'science': 96, 'social': 90, 'total': 461}]
    return render_template("sslcclassmarkpg.html",header_div=header,records=datas,cls=cls,length=len(cls),len2=len(datas))

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
