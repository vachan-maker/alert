import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now get the variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


