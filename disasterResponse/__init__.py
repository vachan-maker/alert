#where we initialise application and bring together components
# tells python this is a package and initialises everything we need for the app
from flask import Flask
import os
from supabase import create_client
from .config import SUPABASE_URL, SUPABASE_KEY
from flask_jwt_extended import JWTManager
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('SUPABASE_JWT_SECRET')
app.config['JWT_ALGORITHM'] = os.getenv('')


jwt = JWTManager(app)
#creating instance of the database

from disasterResponse import routes
#prevent circular import
