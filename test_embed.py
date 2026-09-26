# import yaml
# with open("catalog.yaml") as f:
#     catalog = yaml.safe_load(f)
# print(catalog["tables"]["orders"]["description"])

import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ["GEMINI_API_KEY"]

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={API_KEY}"

body = {
    "content": {"parts": [{"text": "A customer's profile with signup details"}]}
}

response = requests.post(url, json=body)
data = response.json()
embedding = data["embedding"]["values"]

print(len(embedding))
print(embedding[:5])


# Endpoint embedContent hai — generateContent se alag kaam karta hai, isliye alag URL
# body simple hai — sirf content.parts.text, koi generationConfig/responseSchema ki zarurat nahi (embeddings ek fixed-format output dete hain, JSON schema batane ki zarurat nahi)
# Response me data["embedding"]["values"] ek list of decimal numbers milegi