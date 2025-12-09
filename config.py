# config.py
import os
import openai

API_KEY = os.getenv("OPENAI_API_KEY")      
MODEL_NAME = "gpt-4"
MAX_ITERATIONS = 6
PREFERRED_WORD_TARGET = 200
# client = openai.OpenAI(api_key=API_KEY)
openai.apikey = API_KEY
