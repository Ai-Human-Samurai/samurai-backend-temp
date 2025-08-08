import os
from dotenv import load_dotenv
import openai
from core.config import settings 

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your-google-key")

openai.api_key = OPENAI_API_KEY
openai_client = openai
