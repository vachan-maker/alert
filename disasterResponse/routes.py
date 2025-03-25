from urllib import response
from flask import render_template, request, jsonify, session, redirect,url_for,flash
from dotenv import load_dotenv
from functools import wraps
import os
# import openmeteo_requests

import requests
from disasterResponse import supabase
from disasterResponse import app
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
AUTH_URL = f"{SUPABASE_URL}/auth/v1"


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email and password:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            # print(response)
            if response and response.session.access_token:
                session["user"] = response.session.access_token
                session["user_id"] = response.user.id
                print(session["user_id"])
                return redirect(url_for("dashboard"))
            else:
                return jsonify({"error": "Invalid credentials"}), 401
    return render_template("sign-in.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        response = supabase.auth.sign_up(
    {"email": email, "password": password})
        print(response)
        if response:
            session["user"] = response.session.access_token
            return redirect(url_for("dashboard"))
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    return render_template("register.html")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))  # Redirect to login page if not authenticated
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def dashboard():
    try:
        response = supabase.table("profiles").select("name").eq("id", session["user_id"]).execute()
        global username 
        username = response.data[0]["name"]
        print(response)
    except Exception as e:
        print(e)
    return render_template("index.html",name=username)

@app.route("/sos",methods=["POST"]) 
def sos():
    try:
        longitude = request.form.get("longitude")
        latitude = request.form.get("latitude")
        selected_emergency = request.form.get("emergency")
        phone = request.form.get("phone")
        name = request.form.get("name")
        response = (
        supabase.table("SOSAlerts")
        .insert({"user_identification": 8921385972, "message": "Pluto", "longitude": longitude, "latitude": latitude, "UserName": username,"distress_type": selected_emergency,"phone-number":phone})  
        .execute())
        flash("SOS Alert sent! Help is on the way!", "success")
        return redirect(url_for("dashboard"))
    except Exception:
        flash("Error sending SOS Alert. Have you enabled location?", "danger")
        return (redirect(url_for("dashboard")))


@app.route("/phone",methods=["POST","GET"])
def phone():
    if request.method == "POST":
        phone = request.form.get("phone")
        response = supabase.auth.sign_in_with_otp({
        'phone': phone,
    })
        session["phone number"] = phone
    return render_template("phone.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/webhook",methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        data = request.json
        print(data)
        return jsonify(data)
    
@app.route("/get_sos_locations", methods=["GET"])
def get_sos_locations():
    try:
        response = supabase.table("SOSAlerts").select("*").execute()
        data = response.data
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/first-aid")
def first_aid():
    return render_template("first-aid.html")