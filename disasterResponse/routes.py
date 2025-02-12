from urllib import response
from flask import render_template, request, jsonify
from dotenv import load_dotenv
import os

import requests
from disasterResponse import supabase
from disasterResponse import app
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
AUTH_URL = f"{SUPABASE_URL}/auth/v1"

@app.route("/sign-in")
def sign_in():
    return render_template("sign-in.html")
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    response = requests.post(AUTH_URL, headers={"apikey": SUPABASE_KEY}, json={"email": email, "password": password})
    return response.json(),response.status_code
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