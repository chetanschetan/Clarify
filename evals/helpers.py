import requests

BASE_URL = "http://127.0.0.1:8000"

def call_ask_endpoint(question: str):
    response = requests.post(f"{BASE_URL}/ask", json={"question": question})
    return response.json()

def rows_match(actual_rows, expected_rows, tolerance=0.01):
    if len(actual_rows) != len(expected_rows):
        return False
    for actual_row, expected_row in zip(actual_rows, expected_rows):
        # sirf last N values compare karo (jitni expected_row me hain)
        actual_tail = actual_row[-len(expected_row):]
        for a, e in zip(actual_tail, expected_row):
            if isinstance(e, (int, float)):
                if abs(float(a) - float(e)) > tolerance:
                    return False
            else:
                if a != e:
                    return False
    return True




# Samjho: actual_row[-len(expected_row):] — agar actual_row ke paas extra columns hain shuru me (jaise id), hum sirf aakhri N columns lete hain jo expected se match karte hain — taaki extra id/email columns issue na banayein. Numbers ke liye tolerance use kiya (chhota rounding-farak allow karta hai).

# Dhyan de: ye fix Problem B (interpretation mismatch) ko theek nahi karega — wo genuinely real mismatch hai (alag customers, alag totals), jo sahi hai ki fail dikhe — kyunki asal me ambiguity hui hai. Comparator sirf column-shape wali superficial galti fix karega.