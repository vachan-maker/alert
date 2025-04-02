from urllib import response
from flask import render_template, request, jsonify, session, redirect,url_for,flash
from dotenv import load_dotenv
from flask_cors import CORS
from pywebpush import webpush, WebPushException
from functools import wraps
import os, json

from urllib.parse import urlparse
# import openmeteo_requests
import requests
from disasterResponse import supabase
from disasterResponse import app
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

AUTH_URL = f"{SUPABASE_URL}/auth/v1"
# WebSocket Listener for Supabase Realtime
# Function to handle new record insertions
def send_notification(sub,message,notification_url):
    try:
        parsed_url = urlparse(sub["endpoint"])
        audience = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        webpush(
            subscription_info=sub,
            data=json.dumps({"title": "Test Notification", "body": message, "url": notification_url}),
            vapid_private_key=os.getenv('VAPID_PRIVATE_KEY'),
            vapid_claims={
                "sub": "mailto:your-email@example.com",  # Use a valid email
                "aud": audience,  # Correct audience for the endpoint
                "vapid_pub": os.getenv('VAPID_PUBLIC_KEY')  # Include the VAPID public key
            })
        # print("Notification sent successfully")
        
        return ({'status': 'success'}), 200
    except WebPushException as e:
        print(f"Error sending notification: {e}")
        return ({'status': 'error', 'message': str(e)}), 500
@app.before_request
def check_session():
    """Refresh session if the token has expired."""
    if request.endpoint in ["login", "logout"]:  # Skip check for login/logout
        return  

    if "user" in session:
        try:
            # Check if the token is still valid
            supabase.auth.get_user(session["user"])
        except:
            # Token expired, try refreshing
            try:
                response = supabase.auth.refresh_session(session["refresh_token"])
                session["user"] = response.session.access_token
                session["refresh_token"] = response.session.refresh_token  # Update refresh token
            except:
                session.clear()  # Clear session if refresh fails
                flash("Session expired, please log in again.", "warning")
                return redirect(url_for("login"))

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        try:
            if email and password:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                print("Supabase Response:", response)
                
                if "error" in response:
                    print("Supabase Error:", response["error"])
                    flash(response["error"]["message"], "error")  
                    return redirect(url_for("login_page"))

                if response.user and not response.user.email_confirmed_at:
                    flash("Please confirm your email before logging in.", "warning")
                    return redirect(url_for("login_page"))

                session["user"] = response.session.access_token
                session["user_id"] = response.user.id

                return redirect(url_for("dashboard"))

        except Exception as e:
            print(f"Login Error: {e}")  # Debugging output
            flash(f"Login failed: {str(e)}", "error")
            return render_template("sign-in.html")
    return render_template("sign-in.html")
@app.route("/logout")
def logout():
    if "user" in session:
        try:
            supabase.auth.sign_out()  # Logs out from Supabase
        except Exception as e:
            print("Logout error:", e)  # Log any errors

    session.clear()  # Clears the Flask session
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        response = supabase.auth.sign_up(
    {"email": email, "password": password})
        print(response)
        if response.user.email_confirmed_at == None:
            flash("Registration successful! Please check your email to confirm your account.", "success")
            return redirect(url_for("login"))
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
        response= (
        supabase.table("SOSAlerts")
        .insert({"user_identification": 8921385972, "message": phone, "longitude": longitude, "latitude": latitude, "UserName": name,"distress_type": selected_emergency,"user_id": session["user_id"]})  
        .execute())
        print(response)
        flash("SOS Alert sent! Help is on the way!", "success")
        return redirect(url_for("dashboard"))
    except Exception as e:
        print(e)
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

@app.route('/webhook', methods=['POST','GET'])
def handle_webhook():
    data = request.json  # Get JSON data from Supabase
    print("Data",data)
    user_id = data['record']['user_id']
    sos_id = data['record']['sos_id']
    sos_alert_url = f"https://alert-zbsh.onrender.com/alert/{sos_id}"
    print("User ID from webhook:", user_id)
    print(user_id)
    response = supabase.table("user_device_tokens").select("device_token").eq("user_id", user_id).execute()
    tokens = [row["device_token"] for row in response.data]
    for token in tokens:
        send_notification(token, "An SOS Alert detected near you.Tap for more info!",sos_alert_url)
    # Process the incoming data (e.g., send push notification)
    return jsonify({"status": "success"}), 200
@app.route("/alert/<alert_id>")
def alert(alert_id):
    try:
        response = supabase.table("SOSAlerts").select("*").eq("id", alert_id).execute()
        data = response.data
        if data:
            return render_template("alert.html", alert=data[0])
        else:
            return jsonify({"error": "Alert not found"}), 404
    except Exception as e:  
        return jsonify({"error": str(e)}), 500  
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
        response = supabase.table("profiles").update({"longitude": longitude, "latitude": latitude}).eq("id", session["user_id"]).execute()
        # print(response)
        return jsonify({"message": "Location updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Route to get the VAPID public key
@app.route('/vapid_public_key')
def vapid_public_key():
    return jsonify({'public_key': os.getenv('VAPID_PUBLIC_KEY')})

# Route to handle subscription
@app.route('/subscribe', methods=['POST'])
def subscribe():
    global subscription
    subscription = request.get_json()
    response = supabase.table("user_device_tokens") \
    .upsert({"user_id": session["user_id"], "device_token": subscription}, on_conflict=["device_token"]) \
    .execute()
    print("SUBSCRIIIBE")
    print(response)
    # response = supabase.table("profiles").update({"sub":subscription}).eq("id", session["user_id"]).execute()
    # responseb = supabase.table("user_device_tokens").insert({"user_id": session["user_id"], "device_token": subscription}).execute()
    # print(session["longitude"],session["latitude"])
    return jsonify({'status': 'success'}), 201

# Route to send a test notification
@app.route('/send_notification', methods=['POST'])

@app.route("/test")
def test():
    return render_template("test.html")
if __name__ == '__main__':
    app.run(debug=True)