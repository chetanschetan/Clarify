import yaml
import json
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ["GEMINI_API_KEY"]
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={API_KEY}"

def get_embedding(text: str):
    body = {"content": {"parts": [{"text": text}]}}
    response = requests.post(url, json=body)
    data = response.json()
    return data["embedding"]["values"]

if __name__ == "__main__":
    with open("catalog.yaml") as f:
        catalog = yaml.safe_load(f)

    table_embeddings = {}

    for table_name, table_info in catalog["tables"].items():
        column_summary = ", ".join(table_info["columns"].keys())
        text_to_embed = f"{table_info['description']}. Columns: {column_summary}"
        
        print(f"Embedding: {table_name}")
        embedding = get_embedding(text_to_embed)
        table_embeddings[table_name] = embedding
        
        time.sleep(2)

    with open("table_embeddings.json", "w") as f:
        json.dump(table_embeddings, f)

    print(f"\nDone. Saved {len(table_embeddings)} table embeddings to table_embeddings.json")