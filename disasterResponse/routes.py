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


@app.route("/signin")
def signin():
    return render_template("sign-in.html")
@app.route("/login",methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
        
    try:
        response = response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        print(response)
        return "You are logged in"
    except Exception as e:
        return "Wrong email or password"
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            response = supabase.auth.sign_up(
    {"email": email, "password": password}
)
            print(response)
            return "You are registered"
        except Exception as e:
            return "User already exists"
    return render_template("register.html")
    
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/sos",methods=["POST"]) 
def sos():
    longitude = request.form.get("longitude")
    latitude = request.form.get("latitude")
    response = (
    supabase.table("SOS Alerts")
    .insert({"user_identification": 8921385972, "message": "Pluto", "longitude": longitude, "latitude": latitude})
    .execute()

)
    
@app.route("/halan")
def halan():
    return render_template("halan.html")