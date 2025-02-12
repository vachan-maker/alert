from flask import render_template, request, jsonify
from disasterResponse import supabase
from disasterResponse import app

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/sos")
def sos():
    response = (
    supabase.table("SOS Alerts")
    .insert({"user_identification": 8921385972, "message": "Pluto"})
    .execute()
)