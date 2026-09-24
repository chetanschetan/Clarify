import pytest
from helpers import call_ask_endpoint, rows_match
from golden_data import GOLDEN_QUERIES
import time

@pytest.mark.parametrize("case", GOLDEN_QUERIES, ids=lambda c: c["id"])
def test_golden_query(case):
    time.sleep(3)  
    response = call_ask_endpoint(case["question"])
    print(f"\nGenerated SQL: {response.get('sql')}")
    print(f"Assumptions: {response.get('assumptions')}")
    
    assert "rows" in response, f"Query failed: {response.get('detail')}"
    assert rows_match(response["rows"], case["expected_rows"]), \
        f"Expected {case['expected_rows']}, got {response['rows']}"

# @pytest.mark.parametrize("case", GOLDEN_QUERIES, ids=...) — ye decorator bolta hai "is function ko GOLDEN_QUERIES list ke har item ke liye alag se chalao, har baar case variable me wo item de do." ids=lambda c: c["id"] sirf test-report me achha naam dikhane ke liye hai (jaise test_golden_query[q1], test_golden_query[q9]), warna generic numbers dikhte.
# assert "rows" in response, f"..." — assert ke baad comma se ek custom message de sakte hain, jo fail hone par dikhega (debugging me help karta hai)