from urllib import response
from flask import send_from_directory
from flask import render_template, request, jsonify, session, redirect,url_for,flash
from dotenv import load_dotenv
from flask_cors import CORS
from pywebpush import webpush, WebPushException
from functools import wraps
import os
import math,json

# import openmeteo_requests

import requests
from disasterResponse import supabase
from disasterResponse import app
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")

AUTH_URL = f"{SUPABASE_URL}/auth/v1"




def send_push_notification(push_token, title, message):
    try:
        webpush(
            subscription_info=push_token,
            data=json.dumps({"title": title, "body": message}),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims='vachan2014carmel@gmail.com'
        )
    except Exception as e:
        print(f"Push failed: {e}")

def send_notifications(push_tokens, title, message):
    for token in push_tokens:
        send_push_notification(token, title, message)
# Haversine formula to calculate distance
def is_within_radius(lat1, lon1, lat2, lon2, radius_km=10):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c <= radius_km

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
@app.route("/sos", methods=["POST"]) 
def sos():
    try:
        longitude = float(request.form.get("longitude"))
        latitude = float(request.form.get("latitude"))
        selected_emergency = request.form.get("emergency")
        phone = request.form.get("phone")
        name = request.form.get("name")

        # Insert SOS alert into database
        response = supabase.table("SOSAlerts").insert({
            "user_identification": 8921385972,
            "message": phone,
            "longitude": longitude,
            "latitude": latitude,
            "UserName": username,
            "distress_type": selected_emergency
        }).execute()

        flash("SOS Alert sent! Help is on the way!", "success")

        # Fetch all users' subscriptions and locations
        users = supabase.table("profiles").select("id, latitude, longitude, sub").execute()
        push_tokens = []

        # Find users within 10km radius
        for user in users.data:
            if user["latitude"] and user["longitude"] and is_within_radius(latitude, longitude, user["latitude"], user["longitude"]):
                if user.get("sub"):  # Check if user has a push subscription
                    push_tokens.append(user["sub"])
                    print(user["sub"])
        # Send push notifications to nearby users
        if push_tokens:
            send_notifications(push_tokens, "Emergency Alert!", f"{name} has triggered an SOS alert near you.")

        return redirect(url_for("dashboard"))

    except Exception as e:
        print(e)
        return redirect(url_for("dashboard"))

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

@app.route("/update_location", methods=["POST"])
def update_location():
    try:
        data = request.get_json()
        longitude = data.get("longitude")
        latitude = data.get("latitude")
        print(longitude,latitude)
        response = supabase.table("profiles").update({"Longitude": longitude, "Latitude": latitude}).eq("id", session["user_id"]).execute()
        print(response)
        return jsonify({"message": "Location updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/vapidPublicKey")
def get_vapid_public_key():
    """Frontend fetches the VAPID public key from here"""
    return jsonify({"publicKey": VAPID_PUBLIC_KEY})

@app.route("/subscribe", methods=["POST"])
def subscribe():
    subscription_data = request.get_json()
    response = supabase.table("profiles").update({"sub":subscription_data}).eq("id", session["user_id"]).execute()
    print(response)
    return jsonify({"message": "Subscription stored!"}), 201

# Route to serve service-worker.js
@app.route('/service-worker.js')
def serve_sw():
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')

