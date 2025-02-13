from urllib import response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask import render_template, request, jsonify, session
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
        print("Hello Vachan!")
        return jsonify({"access_token": token}), 200
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
            return "You are registered"
        except Exception as e:
            return "User already exists"
    return render_template("register.html")
    
@app.route("/")
def home():

    token = session.get("access_token") 
    if token:
        return render_template("index.html")
    else:
        return ("Error")

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