# import requests
# import os
# from dotenv import load_dotenv
# import json

# load_dotenv()
# API_KEY = os.environ["GEMINI_API_KEY"]

# url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={API_KEY}"

# # body = {
# #     "system_instruction": {
# #         "parts": [{"text": "You are a helpful assistant. Always respond in English only, regardless of what language the user writes in."}]
# #     },
# #     "contents": [
# #         {"parts": [{"text": "1 se 5 tak ginti likho"}]}
# #     ],
# #     "generationConfig": {
# #         "thinkingConfig": {
# #             "includeThoughts": True
# #         }
# #     }
# # }


# # body = {
# #     "system_instruction": {
# #         "parts": [{"text": "You are a helpful assistant that always responds in the requested JSON format."}]
# #     },
# #     "contents": [
# #         {"parts": [{"text": "Give me 3 fun facts about the moon."}]}
# #     ],
# #     "generationConfig": {
# #         "responseMimeType": "application/json",
# #         "responseSchema": {
# #             "type": "OBJECT",
# #             "properties": {
# #                 "facts": {
# #                     "type": "ARRAY",
# #                     "items": {"type": "STRING"}
# #                 }
# #             },
# #             "required": ["facts"]
# #         }
# #     }
# # }


# body = {
#     "system_instruction": {
#         "parts": [{"text": "You are a helpful assistant that always responds in the requested JSON format."}]
#     },
#     "contents": [
#         {"parts": [{"text": "Write a SQL query to count all customers. Table name is 'customers', columns are id, first_name, last_name, signup_date."}]}
#     ],
#     "generationConfig": {
#         "responseMimeType": "application/json",
#         "responseSchema": {
#             "type": "OBJECT",
#             "properties": {
#                 "sql": {"type":"STRING"},
#                 "tables_used": {"type":"ARRAY","items":{"type":"STRING"}},
#                 "assumptions": {"type":"ARRAY","items":{"type":"STRING"}}
#             },
#             "required": ["sql","tables_used"]
#         }
#     }
# }

# response = requests.post(url, json=body)
# data = response.json()

# # print(data["candidates"][0]["content"]["parts"][0]["text"])

# raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
# parsed = json.loads(raw_text)
# # print(parsed["facts"])



import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
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

body = {
    "system_instruction": {
        "parts": [{"text": "You are a helpful assistant that always responds in the requested JSON format."}]
    },
    "contents": [
        {"parts": [{"text": f"""
            Database schema:
            {SCHEMA_DESCRIPTION}

            Question: How many completed orders were placed by customers from India in the last 90 days?
            """}]}
    ],
    "generationConfig": {
        "responseMimeType": "application/json",
        "responseSchema": {
            "type": "OBJECT",
            "properties": {
                "sql": {"type": "STRING"},
                "tables_used": {"type": "ARRAY", "items": {"type": "STRING"}},
                "assumptions": {"type": "ARRAY", "items": {"type": "STRING"}}
            },
            "required": ["sql", "tables_used"]
        }
    }
}

response = requests.post(url, json=body)
print(response.json())