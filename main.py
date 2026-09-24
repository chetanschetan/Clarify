from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests, os, json
from dotenv import load_dotenv
import psycopg
import sqlglot
from sqlglot.expressions import Select
import time


load_dotenv()
app = FastAPI()
# conn = psycopg.connect(os.environ["DATABASE_URL"])
conn = psycopg.connect(os.environ["READONLY_DATABASE_URL"])
cur = conn.cursor()
cur.execute("SET statement_timeout = 5000;")
conn.commit()

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

def check_query_cost(sql: str, max_cost: float = 10000.0):
# def check_query_cost(sql: str, max_cost: float = 1.0):
    cur.execute(f"EXPLAIN (FORMAT JSON) {sql}")
    plan = cur.fetchone()[0]
    total_cost = plan[0]["Plan"]["Total Cost"]
    
    if total_cost > max_cost:
        raise ValueError(f"Query too expensive (cost: {total_cost}). Try narrowing your question.")
    
    return total_cost

def add_limit_if_missing(sql: str, max_rows: int = 1000) -> str:
    parsed = sqlglot.parse_one(sql)
    
    if parsed.args.get("limit") is None:
        parsed = parsed.limit(max_rows)
    
    return parsed.sql()

def call_gemini(body):
    for attempt in range(3):
        response = requests.post(url, json=body)
        data = response.json()
        if "candidates" in data:
            return data
        print(f"Attempt {attempt + 1} failed: {data.get('error', {}).get('message')}")
        time.sleep(15)
    raise HTTPException(status_code=503, detail="LLM service unavailable after 3 attempts. Please try again.")

def validate_sql(sql: str):
    parsed = sqlglot.parse(sql)
    
    if len(parsed) != 1:
        raise ValueError("Only a single SQL statement is allowed.")
    
    statement = parsed[0]
    
    if not isinstance(statement, Select):
        raise ValueError("Only SELECT statements are allowed.")
    
    return True

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask(q: Question):
    body = {
        "system_instruction": {
            "parts": [{"text": "You are a helpful assistant that always responds in the requested JSON format. Always use valid PostgreSQL syntax — for example, use INTERVAL '30 days' (number and unit together in one string), not INTERVAL '30' DAYS."}]
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

    # response = requests.post(url, json=body)
    # data = response.json()
    # return data
    data = call_gemini(body)
    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

    if isinstance(raw_text, str):
        parsed = json.loads(raw_text)
    else:
        parsed = raw_text

    try:
        validate_sql(parsed["sql"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    final_sql = add_limit_if_missing(parsed["sql"])
    # cur.execute(final_sql)

    try:
        check_query_cost(final_sql)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except psycopg.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Generated SQL is invalid: {e}")

    try:
        cur.execute(final_sql)
        rows = cur.fetchall()
    except psycopg.errors.QueryCanceled:
        conn.rollback()
        raise HTTPException(status_code=408, detail="Query took too long and was cancelled.")
    except Exception as e:
        conn.rollback()
        raise

    # rows = cur.fetchall()

    parsed["rows"] = rows
    return parsed