from fastapi import FastAPI
from pydantic import BaseModel
import requests, os, json
from dotenv import load_dotenv
import psycopg

load_dotenv()
app = FastAPI()
conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()

API_KEY = os.environ["GEMINI_API_KEY"]
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={API_KEY}"


SCHEMA_DESCRIPTION = """
Tables:
- customers(id, first_name, last_name, email, country, signup_date, is_test_account)
- products(id, name, category, price, created_at)
- orders(id, customer_id, order_date, status, total_amount)
- order_items(id, order_id, product_id, quantity, unit_price)
- refunds(id, order_id, refund_date, amount, reason)
- sessions(id, customer_id, session_start, session_end, device)
"""

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask(q: Question):
    body = {
        "system_instruction": {
            "parts": [{"text": "You are a helpful assistant that always responds in the requested JSON format."}]
        },
        "contents": [
            {"parts": [{"text": f"""
                Database schema:
                {SCHEMA_DESCRIPTION}

                Question: {q.question}
                """}]}
            ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "sql": {"type":"STRING"},
                    "tables_used": {"type":"ARRAY","items":{"type":"STRING"}},
                    "assumptions": {"type":"ARRAY","items":{"type":"STRING"}}
                },
                "required": ["sql","tables_used"]
            }
        }
    }

    response = requests.post(url, json=body)
    data = response.json()
    print(data)
    # return data
    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

    if isinstance(raw_text, str):
        parsed = json.loads(raw_text)
    else:
        parsed = raw_text
    # parsed = json.loads(raw_text)
    cur.execute(parsed["sql"])
    rows = cur.fetchall()

    parsed["rows"] = rows
    return parsed