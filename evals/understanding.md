"Eval" ka matlab kya hai — simple definition

Eval (evaluation ka short form) matlab: "hamara AI system kitna accurately kaam kar raha hai, ye measure karne ka tareeka."

Socho tune ek exam banaya — jisme tujhe pehle se sawaal bhi pata hain, sahi jawab bhi pata hain (kyunki khud banaye the). Ab jab bhi koi student (yahan, hamara AI system) exam deta hai, tu uske answers ko sahi answers se match karta hai, aur ek score nikalta hai: "X% sahi."

Yehi Phase 3 me humne banaya:

Sawaal = tere golden questions ("pichle mahine kitne customers signup hue")
Sahi jawab = jo tune manually database se nikala (431)
Student = hamara /ask endpoint (AI se SQL banake execute karta hai)
Grading = rows_match() function jo compare karta hai
Report card = run_eval.py ka output (PASS: 2/3, SYNTAX_ERROR: 1/3)
Hum ye kyun banaya — do wajahein
Wajah 1: "Bina naapे, tu improve nahi kar sakta"

Socho agar tu bina eval ke seedha Phase 4 (RAG) shuru kar deta. Tu schema-catalog banata, embeddings jodta, prompt badalta — aur phir manually 2-3 sawaal poochh ke dekhta "achha lag raha hai." Par tujhe pata hi nahi chalega:

Kya RAG lagane se accuracy genuinely badhi?
Ya sirf tujhe lucky sawaal mile jo pehle bhi sahi ho jate?
Kya koi purana kaam karta sawaal ab tootne laga?

Bina eval ke, tu "vibes" se develop kar raha hota — bilkul wahi cheez jo humne Part 1 me discuss ki thi ki avoid karni hai. Eval ke saath, tu exact number bata sakta hai: "RAG lagane se pehle 67% pass tha, lagane ke baad 85% ho gaya."

Wajah 2: Resume/interview ke liye — numbers, na ki claims

Yaad kar humne bahut pehle discuss kiya tha: "Reduced silently-incorrect answers from 34% to 6%" jaisi line resume pe bahut strong lagti hai. Ye line sirf tabhi likh sakta hai jab tere paas eval ho — jisse tu before/after compare kar sake. Bina eval ke, tu sirf keh sakta hai "maine RAG add kiya, better lagta hai" — jo weak hai, unverifiable hai.

Iska use kya hai — abhi, aur aage

Abhi, Phase 4 ke context me: jab hum RAG add karenge (poora schema bhejne ki jagah sirf relevant tables bhejna), hum yehi same eval script (run_eval.py) dobara chalayenge — same golden queries pe — aur dekhenge:

Kya PASS percentage badhi ya wahi rahi?
Kya SYNTAX_ERROR wali category kam hui?
Kitne tokens bache (kyunki poora schema nahi bheja)?

Aage, poore project me: Phase 5 (ambiguity engine), Phase 7 (repair loop) — har naye feature ke baad, hum wahi eval chalayenge, dekhne ke liye "is naye feature ne genuinely help ki ya nahi." Eval hamara permanent measuring tape hai — jo bhi hum banayenge, usko isی se check karenge.

Ek analogy jo shayad help kare

Socho tu gym jaa raha hai weight kam karne. Eval = weighing scale. Bina scale ke, tu roz gym jaake "lagta hai weight kam ho raha hai" bol sakta hai — par pata nahi chalega genuinely ho raha hai ya nahi. Scale (eval) se tu exact number dekhta hai har hafte, aur confirm hota hai kaunsa exercise (feature) kaam kar raha hai.