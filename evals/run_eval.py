# Task 3.4 — categorized report script, jo pehle diya tha wahi structure, ab stable 3-query set (Q1, Q2, Q4) pe.

import time
from helpers import call_ask_endpoint, rows_match
from golden_data import GOLDEN_QUERIES

def categorize(response, expected_rows):
    if "rows" not in response:
        detail = response.get("detail", "").lower()
        if "unavailable" in detail or "attempts" in detail:
            return "INFRA_FAILURE"
        elif "invalid" in detail or "syntax" in detail:
            return "SYNTAX_ERROR"
        elif "select" in detail:
            return "GUARDRAIL_BLOCKED"
        else:
            return "OTHER_ERROR"

    if rows_match(response["rows"], expected_rows):
        return "PASS"

    return "MISMATCH"

results = []
for case in GOLDEN_QUERIES:
    time.sleep(1)
    response = call_ask_endpoint(case["question"])
    category = categorize(response, case["expected_rows"])
    results.append({"id": case["id"], "category": category})
    print(f"{case['id']}: {category}")

print("\n--- Summary ---")
total = len(results)
for cat in ["PASS", "MISMATCH", "INFRA_FAILURE", "SYNTAX_ERROR", "GUARDRAIL_BLOCKED", "OTHER_ERROR"]:
    count = sum(1 for r in results if r["category"] == cat)
    if count:
        print(f"{cat}: {count}/{total} ({100*count/total:.0f}%)")

        # Naya yahan sirf itna hai: ye ek plain script hai (pytest nahi) — isliye ye kabhi "fail" nahi hoga jaise pytest karta hai, sirf report print karega. Yahi farak hai — pytest tujhe bolta hai "kuch galat hai," ye script tujhe bolta hai "yahan kya hua, categorized."