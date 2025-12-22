import os
from dotenv import load_dotenv
load_dotenv()
YOUTUBE_KEY=os.getenv("YOUTUBE_API_KEY","")
DISCOURSE_URL="https://community.n8n.io/latest.json"
SEARCH_TERMS=[
    "n8n workflow",
    "n8n automation", 
    "n8n tutorial",
    "n8n integration"
]
COUNTRIES=["US","IN"]
DATA_FILE="workflows.json"