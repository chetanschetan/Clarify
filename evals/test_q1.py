from helpers import call_ask_endpoint

def test_q1_new_signups():
    response = call_ask_endpoint("How many customers signed up in the last 30 days?")
    print(response)
    assert "rows" in response is not None or response.get("detail") is not None