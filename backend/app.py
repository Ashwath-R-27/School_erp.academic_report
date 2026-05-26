from flask import Flask,render_template,request

app = Flask(__name__)

@app.route("/")
def first():
    return render_template("home.html")

@app.route("/HSC_2026")
def hscmark():
    return render_template("hscmarkpg.html")

if __name__ == '__main__':
    app.run(debug=True)