GOLDEN_QUERIES = [
        {
            "id": "q1",
            "question": "Pichle calendar month me kitne naye customers signup hue?",
            "expected_rows": [[425]],  # jo bhi actual number aaya
        },
        {
            "id": "q2",
            "question": "Pichle calendar month me total revenue kitna tha? (refunded orders exclude karke)",
            "expected_rows": [[1016654.01]],  # jo bhi actual number aaya
        },
        # {
        #         "id": "q3",
        #         "question": "All-time top 10 customers by total spend",
        #         "expected_rows": [["Maureen","Harrison",14870.36],["Andrea","Campbell",13983.92],["Hunter","Kennedy",13539.95],["Antonio","Patterson",13001.17],["Heather","Conner",12853.94],["Ryan","Greene",12813.71],["Jacob","Dominguez",12798.46],["Tina","May",14752.36],["Jonathan","Mckenzie",12489.14],["Shelley","Phillips",12366.44],["Sandra","Velasquez",12270.56]],  # jo bhi actual number aaya
        # },
        {
                "id": "q4",
                "question": "Last 30 din me sabse zyada bika product kaunsa hai (units)?",
                "expected_rows": [["Wall Candidate", 39]],  # jo bhi actual number aaya
        }
]


# Q1 — likely "time drift," genuine bug nahi

# Expected [[412]], got [[425]]

# Yaad kar maine pehle warn kiya tha — "pichla calendar month" ek moving target hai. Jab tune Phase 0 me 412 nikala tha, "pichla mahina" koi specific mahina tha (jaise August). Ab jab tune test chalaya, agar naya calendar month shuru ho chuka hai (ya kuch dinon ka farak hai), "pichla mahina" khud badal chuka hai — matlab system sahi answer de raha hai, bas naye "pichle mahine" ka.

# Verify karne ka tareeka: wahi manual SQL query abhi dobara chala:

# powershell
# docker compose exec db psql -U clarify -d clarify -c "SELECT COUNT(*) FROM customers WHERE signup_date >= date_trunc('month', current_date - interval '1 month') AND signup_date < date_trunc('month', current_date);"

# Agar ye 425 deta hai, confirm ho jayega ye time-drift tha, model ka bug nahi — bas humara golden_data.py stale ho gaya. Design lesson: relative-date queries (jaise "last month") golden-set me risky hain kyunki unka "sahi answer" waqt ke saath badalta rehta hai — is baat ko note karna zaroori hai docs/decisions/ me.

# Q2 — Passed, achhi baat

# Decimal type ka comparison bhi kaam kar gaya, koi issue nahi.

# Q3 — Ye sabse interesting hai, do alag problems ek saath

# Problem A — Comparator bahut strict hai (superficial issue)

# Dekh model ka result: [id, first_name, last_name, email, total_spent] — 5 columns. Tera expected: [first_name, last_name, total_spent] — 3 columns. Tune kabhi bola hi nahi model ko "sirf ye 3 columns do" — model ne apni marzi se id aur email bhi jod diye (reasonable hai, tune specify nahi kiya). Hamara rows_match() (jo == use karta hai) column-shape match bhi maangta hai — jo bahut strict hai, is case me galat expectation hai.

# Problem B — Genuine interpretation mismatch (deep issue, ye asli discovery hai)

# Numbers bhi alag hain — jaise "Ryan Greene" tera expected me 15807.07 tha, model ne diya 12813.71. Aur customers ki list bhi alag hai (model ke result me "Jonathan Mckenzie," "Shelley Phillips" hain jo tere expected me nahi the; tere "Tina May," "Kelly Norman" model ke result me nahi hain).

# Wajah: Yaad kar Phase 0 me humne note kiya tha — Q3 "gross spend" (refunds included) use kar raha tha. Par model ne is baar khud filter laga diya (jaisa humne Phase 1 me bhi dekha tha) — sirf status = 'completed' orders count kiye, refunded/cancelled exclude kiye. Ye bilkul same "gross vs net" ambiguity hai jo humne khud already discover ki thi (phase0-golden-queries.md me note bhi kiya tha) — ab wo empirically reproduce ho gayi hai, exact numbers ke saath.

# Ye Q3 ka fail "bug" nahi hai — ye tere project ka thesis, live prove ho raha hai.

# Q4 — Same syntax bug, dusri baar

# INTERVAL '30' DAYS — exact wahi error jo pehle bhi aaya tha (single-test run me). Ab do alag independent occurrences mil chuke hain, dono "last 30 days" jaise phrasing ke saath. Ye ab random glitch nahi lagta — ek pattern lagta hai ki model specifically "N days" wale sawaal pe is galat syntax ki taraf jhukta hai.

# Ye actionable hai — yaad kar maine ek optional prompt-fix suggest kiya tha pehle. Ab do occurrences ke saath, ye karna chahiye, deferred nahi:

# python
# "... Always use valid PostgreSQL syntax — for example, use INTERVAL '30 days' (number and unit together in one string), not INTERVAL '30' DAYS."



# Ab plan — teen fixes, is order me

# 1. Q1 fix — manual SQL dobara chala, golden_data.py me 412 ko naye actual number se update kar (jo bhi aaye)

# 2. Q4 mitigation — system_instruction me upar wali line jod, taaki ye specific bug kam ho (guarantee nahi, par frequency kam hogi)

# 3. Comparator ko smarter banana — Q3 ka Problem A fix karne ke liye. Ye zaroori hai kyunki abhi hamara comparator bahut naive hai. Behtar approach:

# python
# def rows_match(actual_rows, expected_rows, tolerance=0.01):
#     if len(actual_rows) != len(expected_rows):
#         return False
#     for actual_row, expected_row in zip(actual_rows, expected_rows):
#         # sirf last N values compare karo (jitni expected_row me hain)
#         actual_tail = actual_row[-len(expected_row):]
#         for a, e in zip(actual_tail, expected_row):
#             if isinstance(e, (int, float)):
#                 if abs(float(a) - float(e)) > tolerance:
#                     return False
#             else:
#                 if a != e:
#                     return False
#     return True

# Samjho: actual_row[-len(expected_row):] — agar actual_row ke paas extra columns hain shuru me (jaise id), hum sirf aakhri N columns lete hain jo expected se match karte hain — taaki extra id/email columns issue na banayein. Numbers ke liye tolerance use kiya (chhota rounding-farak allow karta hai).

# Dhyan de: ye fix Problem B (interpretation mismatch) ko theek nahi karega — wo genuinely real mismatch hai (alag customers, alag totals), jo sahi hai ki fail dikhe — kyunki asal me ambiguity hui hai. Comparator sirf column-shape wali superficial galti fix karega.

# ## Q3 — "All-time top 10 customers by total spend"
# Status: EXCLUDED from exact-match eval — model output non-deterministic
# across independent calls (confirmed 3x): sometimes excludes cancelled
# orders, sometimes doesn't, sometimes includes test accounts, sometimes
# doesn't — despite identical prompt. This is itself the strongest empirical
# evidence yet for Phase 5's necessity. Tracked separately, not scored
# pass/fail until ambiguity-detection exists.