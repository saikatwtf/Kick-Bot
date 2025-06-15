import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Bot information
BOT_USERNAME = None  # Will be set during startup