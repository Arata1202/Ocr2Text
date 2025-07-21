import os
from dotenv import load_dotenv

load_dotenv()

PROMPT = os.getenv('PROMPT', '')
