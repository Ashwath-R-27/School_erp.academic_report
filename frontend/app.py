import argparse
import os

import requests
from dashboard_config import DASHBOARD_CONFIGS
from flask import Flask, jsonify, redirect, request, render_template,send_file, url_for
from form_response_generator import build_student_pdf, build_sslc_student_pdf
from requests.models import HTTPError

app = Flask(__name__)
parser = argparse.ArgumentParser(description="A simple CLI tool.")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")


parser.add_argument(
    "--debug", action="store_true", help="Enable debug mode with verbose logging"
)
args = parser.parse_args()
debug_mode = args.debug


def get_data_from_backend(REQUEST_ENDPOINT):
    try:
        response = requests.get(BACKEND_URL + REQUEST_ENDPOINT)
        return response.json()

    except HTTPError:
        return []


@app.route("/init_db")
def initialize_db():

    hsc_res = get_data_from_backend("/import_hsc")
    print("HSC Import Results:", hsc_res)

    sslc_res = get_data_from_backend("/import_sslc?class_char=A")
    print("SSLC Import Results:", sslc_res)

    return jsonify({"hsc_initialization": hsc_res, "sslc_initialization": sslc_res})


@app.route("/init_mock")
def initialize_mock_db():

    hsc_res = get_data_from_backend("/import_hsc_mock")
    print("HSC Import Results:", hsc_res)

    sslc_res = get_data_from_backend("/import_sslc?class_char=A")
    print("SSLC Import Results:", sslc_res)

    return jsonify({"hsc_initialization": hsc_res, "sslc_initialization": sslc_res})


def header_div():
    logo_url = url_for("static", filename="logo.avif")
    header = f""" <div class="header">
        <div class="logo"><a href="#"><img src="{logo_url}" id="logo"></a></div>
        <div class="header_content">
            <div class="header_text_1">SVGV MATRICULATION HIGHER SECONDARY SCHOOL</div>
        </div>
    </div>"""
    return header


def footer_div():
    footer = """ <div class="footer">
                © 2026 SVGV Matriculation Higher Secondary School, Examination
                Results
            </div> """
    return footer


def hscgroups():
    grpdtls = [
        {
            "name": "COMPUTER SCIENCE + MATHS",
            "code": "csc",
            "sub1": "PHY",
            "sub2": "CHEM",
            "sub3": "CSC",
            "sub4": "MATHS",
        },
        {
            "name": "BIOLOGY + MATHS",
            "code": "biomat",
            "sub1": "PHY",
            "sub2": "CHEM",
            "sub3": "BIO",
            "sub4": "MATHS",
        },
        {
            "name": "BIOLOGY + COMPUTER SCIENCE",
            "code": "biocs",
            "sub1": "PHY",
            "sub2": "CHEM",
            "sub3": "BIO",
            "sub4": "CSC",
        },
        {
            "name": "ARTS + COMPUTER APPLICATION",
            "code": "artsca",
            "sub1": "ECO",
            "sub2": "COM",
            "sub3": "ACC",
            "sub4": "CA",
        },
        {
            "name": "ARTS + BUSINESS MATHEMATICS",
            "code": "artsbm",
            "sub1": "ECO",
            "sub2": "COM",
            "sub3": "ACC",
            "sub4": "BM",
        },
        {
            "name": "BASIC MECHANICAL ENGINEERING",
            "code": "bme",
            "sub1": "MATHS",
            "sub2": "BME (THY)",
            "sub3": "BME (PRT)",
            "sub4": "ES",
        },
    ]
    return grpdtls


@app.route("/")
def first():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@app.route("/dashboard/<path:page>")
def dashboard(page="main"):
    config = DASHBOARD_CONFIGS.get(page, DASHBOARD_CONFIGS["main"])
    return render_template("dashboard.html", config=config)


@app.route("/login")
def loginpg():
    header = header_div()
    return render_template("login.html", header_div=header, footer_div=footer_div())


@app.route("/home")
def home():
    header = header_div()
    return render_template("home.html", header_div=header, footer_div=footer_div())


@app.route("/HSC_2026")
def hscmark():
    header = header_div()
    datas=[]
    data = get_data_from_backend("/hsc/toppers?limit=15")
    for i in data:
        if i['rank']<6:
            datas.append(i)
        else:
            break
    sub_first_marks = get_data_from_backend("/hsc/subject-first-marks")
    return render_template(
        "hscmarkpg.html",
        header_div=header,
        top_scorers=datas,
        len1=len(datas),
        sub_marks=sub_first_marks,
        footer_div=footer_div(),
    )


@app.route("/SSLC_2026")
def sslcmark():
    header = header_div()
    datas = []
    data = get_data_from_backend("/sslc/toppers?limit=15")
    for i in data:
        if i['rank']<6:
            datas.append(i)
        else:
            break
    sub_first_marks = get_data_from_backend("/sslc/subject-first-marks")
    return render_template(
        "sslcmarkpg.html",
        header_div=header,
        top_scorers=datas,
        len1=len(datas),
        sub_marks=sub_first_marks,
        footer_div=footer_div(),
    )


@app.route("/HSC_2026/Marks/Group")
def hscgrpwisemarks():
    groups = hscgroups()
    datas = []
    for group in groups:
        datas.extend(
            get_data_from_backend(f"/hsc/groupwise?group_name={group['code']}")["datas"]
        )
    header = header_div()
    return render_template(
        "hscgrpmark.html",
        header_div=header,
        records=datas,
        groups=groups,
        footer_div=footer_div(),
    )


@app.route("/HSC_2026/Marks/Class")
def hscclasswisemarks():
    classes=[]
    cls = get_data_from_backend("/hsc/sections")
    for sec in cls:
        classes.append(sec['sec'])
    datas = []
    for _class in classes:
        datas.extend(get_data_from_backend(f"/hsc/classwise?class_name={_class}"))
    header = header_div()
    return render_template(
        "hscclsmarkpg.html",
        header_div=header,
        records=datas,
        cls=cls,
        footer_div=footer_div(),
    )


@app.route("/SSLC_2026/Marks")
def sslcclassmark():
    header = header_div()
    cls = ["A", "B", "C", "D", "E"]
    datas = get_data_from_backend("/sslc/toppers?limit=100")
    return render_template(
        "sslcclassmarkpg.html",
        header_div=header,
        records=datas,
        cls=cls,
        length=len(cls),
        len2=len(datas),
        footer_div=footer_div(),
    )


@app.route("/HSC_2026/StudForm")
def hscstudformpg():
    header = header_div()
    cls_data=[{'class': 'A1', 'groups': ['csc', 'biomat']}, {'class': 'A', 'groups': ['csc', 'biomat']}, {'class': 'B', 'groups': ['biomat', 'biocs']}, {'class': 'C', 'groups': ['csc']}, {'class': 'D', 'groups': ['csc']}, {'class': 'E', 'groups': ['artsca', 'artsbm']}, {'class': 'F', 'groups': ['artsca']}, {'class': 'G1', 'groups': ['bme']}, {'class': 'G2', 'groups': ['bme']}]
    return render_template(
        "studform.html", header_div=header,class_data=cls_data, key="hsc", footer_div=footer_div()
    )


@app.route("/SSLC_2026/StudForm")
def sslcstudformpg():
    header = header_div()
    return render_template(
        "studform.html", header_div=header, key="sslc", footer_div=footer_div()
    )


@app.route("/HSC_2026/Report")
def hscreportfetch():
    header = header_div()
    return render_template(
        "hscreportpg.html", header_div=header, footer_div=footer_div()
    )


@app.route("/SSLC_2026/Report")
def sslcreportfetch():
    header = header_div()
    return render_template(
        "sslcreportpg.html", header_div=header, footer_div=footer_div()
    )

@app.route("/HSC/form/submit", methods=["POST"])
def proxy_submit_hsc():
    try:
        response = requests.post(
            BACKEND_URL + "/submit/hsc",
            data=request.form
        )
        return jsonify(response.json()), response.status_code
    except Exception:
        return jsonify({"detail": "Service is currently unavailable. Please try again later."}), 502


@app.route("/submit/sslc", methods=["POST"])
def proxy_submit_sslc():
    try:
        response = requests.post(
            BACKEND_URL + "/submit/sslc",
            data=request.form
        )
        return jsonify(response.json()), response.status_code
    except Exception:
        return jsonify({"detail": "Service is currently unavailable. Please try again later."}), 502

def reponse_page(cls):
    datas = get_data_from_backend(f'/{cls}/student-data')
    count = {}
    for student in datas:
        cls = student["class"]
        count[cls] = count.get(cls, 0) + 1
    count = dict(sorted(count.items()))
    count['TOTAL']=sum(count.values())
    return count

@app.route('/HSC_2026/StudForm/Responses')
def hsc_response():
    notice=""
    return render_template('formresponses.html',title="HSC Student Details",notice=notice,response=reponse_page('hsc'))


@app.route('/SSLC_2026/StudForm/Responses')
def sslc_response():
    notice=""
    return render_template('formresponses.html',title="SSLC Student Details",notice=notice,response=reponse_page('sslc'))

@app.route("/HSC/ClassDetails")
def classentry():
    return render_template("clsentrypg.html",header_div=header_div(),footer_div=footer_div())

@app.route('/hsc-class-details/submit', methods=['POST'])
def proxy_class_details():
    try:
        resp = requests.post(
            BACKEND_URL + '/hsc-class-details/submit',
            json=request.get_json(),
            timeout=10
        )
        return jsonify(resp.json()), resp.status_code
    except requests.RequestException:
        return jsonify({'detail': 'Backend unreachable'}), 502

@app.route("/HSC_2026/StudDetails/PDF")
def hsc_student_details_pdf():
    """
    Fetches student data and class counts from the backend,
    generates a PDF, and sends it as a download.
    """
    try:
        students = get_data_from_backend("/hsc/student-data")
        if not students:
            return jsonify({"detail": "No student data found."}), 404

        # Build class counts from backend or derive from student list
        raw_counts = get_data_from_backend("/hsc/class-counts")  # expects [{"class":"A","count":6}, ...]
        if isinstance(raw_counts, list) and raw_counts:
            class_counts = {item["class"]: item["count"] for item in raw_counts}
        else:
            # Fallback: derive counts from the student list itself
            from collections import Counter
            class_counts = dict(Counter(s["class"] for s in students))

        pdf_buffer = build_student_pdf(students, class_counts)
        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="HSC_Student_Details.pdf",
        )
    except Exception as e:
        app.logger.error(f"PDF generation failed: {e}", exc_info=True)
        return jsonify({"detail": "PDF generation failed."}), 500

@app.route("/SSLC_2026/StudDetails/PDF")
def sslc_student_details_pdf():
    """
    Fetches SSLC student data and class counts from the backend,
    generates a PDF, and sends it as a download.
    """
    try:
        students = get_data_from_backend("/sslc/student-data")
        if not students:
            return jsonify({"detail": "No student data found."}), 404

        raw_counts = get_data_from_backend("/sslc/class-counts")  # expects [{"class":"A","count":40}, ...]
        if isinstance(raw_counts, list) and raw_counts:
            class_counts = {item["class"]: item["count"] for item in raw_counts}
        else:
            from collections import Counter
            class_counts = dict(Counter(s["class"] for s in students))

        pdf_buffer = build_sslc_student_pdf(students, class_counts)
        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="SSLC_Student_Details.pdf",
        )
    except Exception as e:
        app.logger.error(f"PDF generation failed: {e}", exc_info=True)
        return jsonify({"detail": "PDF generation failed."}), 500

if __name__ == "__main__":
    if debug_mode:
        app.run(host="0.0.0.0", port=5001, debug=True)
    else:
        app.run(host="0.0.0.0", port=5000, debug=True)
