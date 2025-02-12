import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now get the variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Debug: Check if variables are loaded
print("SUPABASE_URL:", SUPABASE_URL)
print("SUPABASE_KEY:", SUPABASE_KEY)
