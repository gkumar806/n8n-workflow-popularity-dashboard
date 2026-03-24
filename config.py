import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_KEY = os.getenv("YOUTUBE_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
DISCOURSE_URL = "https://community.n8n.io"
COUNTRIES = ["IN", "US"]