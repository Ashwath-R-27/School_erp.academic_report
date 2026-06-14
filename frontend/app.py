import os

import argparse
import requests
from flask import Flask, jsonify, redirect, render_template, url_for
from requests.models import HTTPError

app = Flask(__name__)
parser = argparse.ArgumentParser(description="A simple CLI tool.")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")


    
parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug mode with verbose logging"
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
    logo_url = url_for("static", filename="logo.png")
    header = f""" <div class="header">
        <div class="logo"><a href="#"><img src="{logo_url}" id="logo"></a></div>
        <div class="header_content">
            <div class="header_text_1">SVGV MATRICULATION HIGHER SECONDARY SCHOOL</div>
        </div>
    </div>"""
    return header


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
            "name": "ARTS + ACCOUNTANCY",
            "code": "artsbm",
            "sub1": "ECO",
            "sub2": "COM",
            "sub3": "ACC",
            "sub4": "BM",
        },
        {
            "name": "ARTS + CA",
            "code": "artsca",
            "sub1": "ECO",
            "sub2": "COM",
            "sub3": "ACC",
            "sub4": "CA",
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
    return redirect(url_for("loginpg"))


@app.route("/login")
def loginpg():
    header = header_div()
    return render_template("login.html", header_div=header)


@app.route("/register")
def registerpg():
    header = header_div()
    return render_template("register.html", header_div=header)


@app.route("/home")
def home():
    header = header_div()
    return render_template("home.html", header_div=header)


@app.route("/HSC_2026")
def hscmark():
    header = header_div()
    datas = get_data_from_backend("/hsc/toppers?limit=5")
    sub_first_marks = get_data_from_backend("/hsc/subject-first-marks")
    return render_template(
        "hscmarkpg.html",
        header_div=header,
        top_scorers=datas,
        len1=len(datas),
        sub_marks=sub_first_marks,
    )


@app.route("/SSLC_2026")
def sslcmark():
    header = header_div()
    datas = get_data_from_backend("/sslc/toppers?limit=5")
    sub_first_marks = get_data_from_backend("/sslc/subject-first-marks")
    return render_template(
        "sslcmarkpg.html",
        header_div=header,
        top_scorers=datas,
        len1=len(datas),
        sub_marks=sub_first_marks,
    )


@app.route("/HSC_2026/Marks/Group")
def hscgrpwisemarks():
    datas = get_data_from_backend("/hsc/toppers?limit=50")
    header = header_div()
    groups = hscgroups()
    return render_template(
        "hscgrpmark.html", header_div=header, records=datas, groups=groups
    )


@app.route("/HSC_2026/Marks/Class")
def hscclasswisemarks():
    cls = [
        {
            "sec": "A1",
            "grp": [
                {
                    "name": "COMPUTER SCIENCE + MATHS",
                    "code": "csc",
                    "sub1": "PHY",
                    "sub2": "CHEM",
                    "sub3": "COMP",
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
            ],
        },
        {
            "sec": "A",
            "grp": [
                {
                    "name": "COMPUTER SCIENCE + MATHS",
                    "code": "csc",
                    "sub1": "PHY",
                    "sub2": "CHEM",
                    "sub3": "COMP",
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
            ],
        },
    ]
    datas = get_data_from_backend("/hsc/toppers?limit=50")
    header = header_div()
    return render_template(
        "hscclsmarkpg.html",
        header_div=header,
        records=datas,
        cls=cls,
        length=len(cls),
        len1=len(cls[0]["grp"]),
        len2=len(datas),
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
    )


@app.route("/HSC_2026/StudForm")
def hscstudformpg():
    header = header_div()
    return render_template("studform.html", header_div=header, key="hsc")


@app.route("/SSLC_2026/StudForm")
def sslcstudformpg():
    header = header_div()
    return render_template("studform.html", header_div=header, key="sslc")


if __name__ == "__main__":
    if debug_mode:
        app.run(host="0.0.0.0", port=5001, debug=True)
    else:
        app.run(host="0.0.0.0", port=5000, debug=True)
