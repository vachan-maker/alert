from flask import render_template, request, jsonify
from disasterResponse import app

@app.route("/")
def home():
    return render_template("index.html")