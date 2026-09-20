Q1: Pichle calendar month me kitne naye customers signup hue?
Hint: signup_date column use karna hoga, date_trunc('month', ...) function se "is mahine ka pehla din" nikal sakte ho. Try kar khud likhna, phir bhej — main check karunga.

SOl: SELECT COUNT(*) FROM customers
WHERE signup_date >= date_trunc('month', current_date - interval '1 month')
AND signup_date < date_trunc('month', current_date);

    Logic bilkul sahi hai — tune date_trunc('month', ...) ka concept sahi samjha: ye kisi bhi date ko uske mahine ke pehle din pe le aata hai. Toh:

    date_trunc('month', current_date - interval '1 month') = pichle mahine ka pehla din
    date_trunc('month', current_date) = is mahine ka pehla din

-> docker compose exec db psql -U clarify -d clarify -c "SELECT COUNT(*) FROM customers WHERE signup_date >= date_trunc('month', current_date - interval '1 month') AND signup_date < date_trunc('month', current_date);"


Q2: Pichle calendar month me total revenue kitna tha? (refunded orders exclude karke)

Naya concept: SUM() — COUNT() jaisa hi hai, bas ginti karne ki jagah values jod deta hai. SUM(total_amount) sab matching rows ka total_amount add kar dega.

Hint:

Table orders use hoga (jaha total_amount aur order_date dono hain)
Date range wahi pattern jo Q1 me tha (date_trunc)
status != 'refunded' — refunded orders ko exclude karna hai (chahe cancelled include karna hai ya nahi, ye tera decision hai — is query ke liye bas refunded exclude kar, cancelled ko rehne de, taki tu real-world me dekh sake ki kaise choices answer badalte hain)

SOL:
SELECT SUM(total_amount) FROM orders
WHERE order_date >= date_trunc('month', current_date - interval '1 month')
  AND order_date < date_trunc('month', current_date)
  AND status != 'refunded';

        current_date koi column nahi hai — ye ek function/keyword hai

        current_date teri kisi bhi table ka column nahi hai — na orders me, na customers me, kahin nahi. Ye PostgreSQL ka apna built-in keyword hai jo query chalne ke waqt system ki aaj ki date khud provide karta hai — server ke internal clock se.

        Jab bhi Postgres current_date dekhta hai query me, wo usse compute karke ek actual date value se replace kar deta hai, jaise 2026-09-17 — bilkul waise jaise Python me date.today() aaj ki date deta hai, kisi table se nahi.



Q3: All-time top 10 customers by total spend
Yahan problem ye hai: orders table me sirf customer_id hai (ek number), naam nahi. Humein customer ka naam dikhana hai (identify karne ke liye), par spend orders table se aata hai. Do tables ka data ek saath chahiye — yahi JOIN ka kaam hai.

SOL: SELECT c.first_name, c.last_name, SUM(o.total_amount) AS total_spend
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.first_name, c.last_name
ORDER BY total_spend DESC
LIMIT 10;

    Ek zaroori decision jo tujhe lena hai — refund wapas subtract karega?

    Ye query abhi "total spend" ko orders.total_amount se le rahi hai — refunded orders bhi count ho rahe hain, kyunki humne koi WHERE status != 'refunded' nahi lagaya. Ye ek ambiguity ka real example hai jo tera project handle karega! Do valid interpretations:

    A) Total spend = jo bhi order kiya, chahe refund ho gaya ho (gross)
    B) Total spend = jo abhi tak actually kharch hua hai, refunded minus karke (net)

    Abhi ke liye simple rakh — Option A (koi filter nahi), aur is decision ko note kar le apne golden.md file me ek line comment ki tarah, jaise:

    Note: refunded orders included as "spend" here (gross). 
    Alag interpretation ho sakta hai — ye ambiguity ka example hai jo Phase 5 me formally handle hoga.


Q4: Last 90 days ke top 10 customers by number of orders
Naya cheez: "last 90 days" (rolling window) Q1/Q2 ke "last calendar month" (date_trunc) se alag hai. Rolling window ke liye simple pattern hai:
Ye seedha "aaj se 90 din peeche" bolta hai — koi calendar-month rounding nahi, bas seedha subtract.

SOL: SELECT c.first_name, c.last_name, COUNT(o.id) AS order_count
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE order_date >= current_date - interval '90 days'
GROUP BY c.id, c.first_name, c.last_name
ORDER BY order_count DESC
LIMIT 10;

-> 
 first_name | last_name  | order_count 
------------+------------+-------------
 Heather    | Whitehead  |           6
 Angela     | Tate       |           5
 Patricia   | Mcpherson  |           5
 Ivan       | Lewis      |           5
 Katherine  | Logan      |           5
 Paul       | Crawford   |           5
 Cindy      | Cooper     |           5
 Lori       | Villarreal |           5



 Q5: Kaun se customers is mahine aur pichle mahine dono me order kiya (repeat)?

 SOL: SELECT DISTINCT c.first_name, c.last_name
FROM customers c
WHERE c.id IN (
    SELECT customer_id FROM orders 
    WHERE order_date >= date_trunc('month', current_date)
)
AND c.id IN (
    SELECT customer_id FROM orders 
    WHERE order_date >= date_trunc('month', current_date - interval '1 month')
      AND order_date < date_trunc('month', current_date)
);


Q6: Har product category ka refund rate kya hai?
SOL:
SELECT p.category, 
       COUNT(DISTINCT o.id) AS order_count,
       COUNT(DISTINCT CASE WHEN o.status = 'refunded' THEN o.id END) AS refunded_data
FROM order_items AS oi
JOIN orders AS o ON oi.order_id = o.id
JOIN products AS p ON oi.product_id = p.id
GROUP BY category
ORDER BY refunded_data DESC;

    Framework — 5 sawaal, hamesha isi order me pucho
    1. "Final output me kaun se columns chahiye?"

    Pehle answer ka shape socho, query nahi. Yahan: "category ka naam, aur uske saath do numbers (total orders, refunded orders)." Bas itna — abhi SQL mat socho.

    2. "Ye columns kis-kis table me hain?"
    category → products table me hai
    order status (refunded pata karne ke liye) → orders table me hai
    Inko jodne wala pull → order_items (kyunki isi me product_id bhi hai, order_id bhi hai)

    Ye sabse important step hai. Jitni bhi tables tujhe involve karni padti hain (kyunki columns bikhre hain), utne JOINs chahiye honge. Yahan 3 tables involved hain → isliye 2 JOINs (n tables ke liye hamesha n-1 joins).

    3. "In tables ko kaise jodenge — konsa column dono me common hai?"
    Har JOIN ke liye poocho "kaunsa column dono tables me same value rakhta hai":

    order_items.product_id = products.id → yahi link hai
    order_items.order_id = orders.id → yahi doosra link hai

    Bas isi se ON clause ban jaata hai. Ye mechanical hai — ek baar pata chal jaye kaunse columns link karte hain, ON khud likh sakta hai.

    4. "Kya kisi group ke andar count/sum/average chahiye?"
    Agar haan ("har category ka refund rate") → GROUP BY chahiye, aur us column pe jispe grouping karni hai (p.category).

    5. "Kya koi condition-based counting hai?" (yahi CASE WHEN wala part hai)
    Yahan do alag numbers chahiye the: total orders aur sirf refunded orders — ek hi query se, ek hi baar me. Jab bhi tujhe "ek group ke andar, condition ke hisaab se alag-alag count" chahiye ho, turant CASE WHEN yaad kar. Isko aise socho:

    "Normal COUNT(x) sab kuch ginta hai. Agar tujhe sirf kuch specific rows ginni hain (condition ke saath), toh CASE WHEN se un rows ko highlight karo (baaki ko NULL bana do), phir COUNT lagao — NULL automatically ignore ho jaate hain COUNT me."

    Practice trick — khud se "socho, phir likho"

    Agli baar jab koi English sawaal aaye, SQL likhne se pehle ye 5 sawaal khud se poochh, kagaz pe jawab likh (2 min lagenge):

    1. Output me kya chahiye? _______
    2. Kaunse tables involve hain? _______
    3. Wo tables kaise jud़ te hain (common columns)? _______
    4. Grouping chahiye? Kis column pe? _______
    5. Koi condition-based filtering/counting hai? _______

    Jab ye 5 answers likhe ho jayein, SQL likhna sirf translation ban jata hai — tujhe sochna nahi padta "kya likhun", bas apne answers ko syntax me dalna padta hai.

    -> == SQL me nahi chalta
    SQL me comparison single = se hota hai, Python jaisa double == nahi:

    sql
    o.status == 'refund'   -- galat
    o.status = 'refunded'  -- sahi



Q7: Har mahine ka average order value (AOV) kya hai, pichle 6 mahino ka?

SOL: "SELECT date_trunc('month', o.order_date) AS month, AVG(o.total_amount) AS average 
FROM orders o 
WHERE order_date >= date_trunc('month', current_date - interval '6 months') 
and order_date < date_trunc('month',current_date) 
GROUP BY month
ORDER BY month;"

Q8: Kaun se customers ne last 6 mahino me koi order nahi kiya (churned)?
SOL:SELECT c.first_name, c.last_name
FROM customers c
WHERE c.id NOT IN (
    SELECT customer_id FROM orders 
    WHERE order_date >= current_date - interval '6 months'
);

    ⚠️ Ek zaroori gotcha jo abhi seekh lena chahiye: NOT IN ke saath ek hidden trap hai — agar subquery ke result me koi bhi NULL value aa jaye, toh poori query khaali result de degi, bina koi error ke! Yahan orders.customer_id NOT NULL hai (schema me check kar), toh abhi safe hai — par aage jab sessions.customer_id (jo NULL ho sakta hai) jaisi cheez ke saath NOT IN use karega, ye trap tujhe pakad sakta hai. Isliye professional SQL me NOT EXISTS zyada safe maana jata hai NOT IN se — abhi ke liye NOT IN chalega (humara case safe hai), par yaad rakh ye gotcha.

    Ab mera pehle wala sawaal — jawab de

    Maine poocha tha: kya ye query un customers ko bhi "churned" bata degi jinhone kabhi order hi nahi kiya (0-order customers, jo humne ~15% weight se banaye the)?

    Socho: NOT IN subquery sirf wahi customer_ids deta hai jinhone last 6 months me order kiya. Ek customer jisne kabhi bhi order nahi kiya (poore lifetime me 0 orders), wo bhi is subquery ki list me nahi hoga — matlab NOT IN check use bhi "match" kar dega, aur wo tere result me "churned" ki tarah dikhega.

    Par asal me — kya ek customer jisne kabhi order kiya hi nahi, use "churned" (matlab "pehle active tha, ab nahi hai") bolna sahi hai? Ya "churned" sirf unhi ko bolna chahiye jo kisi zamane me active the, phir band ho gaye?



SELECT c.first_name, c.last_name
FROM customers c
WHERE c.id NOT IN (
    SELECT customer_id FROM orders 
    WHERE order_date >= date_trunc('month', current_date - interval '6 months')
)
AND c.id IN (
    SELECT customer_id FROM orders
    -- yahan koi date filter nahi — sirf "kabhi order kiya ho, kisi bhi date pe"
);


    Dhyan de dusre subquery me koi WHERE order_date >= ... nahi hai — matlab "orders table me kahin bhi, kabhi bhi is customer ka koi order ho" (poora lifetime).

    Isse ab wo customers exclude ho jayenge jinhone kabhi order hi nahi kiya (unka orders table me kahin naam hi nahi aayega, isliye dusra IN unhe filter kar dega), aur bacha rahega sirf wo group jo pehle active tha, ab nahi hai — asli "churned" definition.

    "Churn rate seems high (24%) due to uniform-random order date distribution in seed data — real-world data would show recency clustering." Ye bhi ek genuine insight hai jo tu observe kiya — data quality ka commentary, ye achha lagta hai documentation me.



Q9: Country-wise total revenue kya hai (top 5)?
SOL:
select c.country, sum(o.total_amount) as revenue
from customers c
join orders o
on o.customer_id = c.id
group by country
order by revenue desc
limit 5


Q10: Last 30 din me sabse zyada bika product kaunsa hai (units)?

SOL: SELECT p.name, SUM(oi.quantity) AS units_sold
FROM order_items AS oi
JOIN products AS p ON oi.product_id = p.id
JOIN orders AS o ON oi.order_id = o.id
WHERE o.order_date >= current_date - interval '30 days'
GROUP BY p.name
ORDER BY units_sold DESC
LIMIT 1;

    count(o.id) nhi kyunki COUNT(o.id) batata hai kitni baar ye product kisi order me appear hua (matlab kitne alag orders me ye product tha)
    Par tujhe chahiye "units" — matlab total quantity. Agar ek order me kisi product ki quantity = 3 hai, wo 3 units count honi chahiye, 1 nahi.


Q11: Kaun se customers ne ₹10,000+ total spend kiya hai par 3 se kam orders me?

SOL:SELECT c.first_name, c.last_name, 
       SUM(o.total_amount) AS total_spend, 
       COUNT(o.id) AS order_count
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.first_name, c.last_name
HAVING SUM(o.total_amount) >= 10000 AND COUNT(o.id) < 3;

    -> group by ord -> X

    Yahan ord COUNT(o.id) ka alias hai — ek aggregate result, na ki koi actual column jispe group karna chahiye. GROUP BY me hamesha wo columns jaate hain jinke basis pe tu groups banana chahta hai — yahan har customer apna alag group hai, isliye GROUP BY me customer ki identity honi chahiye (c.id, c.first_name, c.last_name), na ki ord (jo khud ek calculated number hai, grouping ka basis nahi).

    Agar GROUP BY ord rakhega, Postgres saare customers jinka order_count same hai (jaise sabhi jinke 2 orders hain), unko ek hi group me daal dega — matlab tu individual customer names khoy dega, sirf "jitne customers ke 2 orders the" wala aggregate milega. Ye bilkul galat result dega tere sawaal ke liye.



Q12: Week ka kaunsa din sabse zyada orders leta hai?
SOL: SELECT TO_CHAR(o.order_date, 'Day') AS day, COUNT(o.id) AS order_count
FROM orders o
GROUP BY day
ORDER BY order_count DESC
LIMIT 1;

    TO_CHAR() — date ko text format me dikhana
    sql
    TO_CHAR(order_date, 'Day')

    Ye kisi bhi date ko uske weekday ka naam de deta hai — jaise 'Monday', 'Tuesday', etc. 'Day' ek format code hai (Postgres ka apna mini-language date formatting ke liye — capital D se poora din-ka-naam milta hai).

Q13: Ek customer ke first aur second order ke beech average kitna time gap hota hai?
SOL: SELECT AVG(second.order_date - first.order_date) AS avg_gap_days
FROM (
    SELECT customer_id, order_date,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_rank
    FROM orders
) first
JOIN (
    SELECT customer_id, order_date,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_rank
    FROM orders
) second
ON first.customer_id = second.customer_id 
AND first.order_rank = 1 
AND second.order_rank = 2;



Q14: Kaunsi product category ka average order value sabse zyada hai?
SOL:
    INTERPRETATION A
SELECT p.category, AVG(o.quantity * o.unit_price) AS average
FROM products p
JOIN order_items o ON o.product_id = p.id
GROUP BY p.category
ORDER BY average DESC;

    INTERPRETATION B
SELECT p.category, AVG(o.quantity) AS average
FROM products p
JOIN order_items o ON o.product_id = p.id
GROUP BY p.category
ORDER BY average DESC;


    ## Ambiguity example (self-discovered during Q14):
    Question: "average order value by category"
    - Interpretation A: monetary value (quantity × unit_price) — average ₹ spent
    - Interpretation B: average quantity/units purchased
    Both are valid readings of "value" without further context. This mirrors 
    the exact "best customer" ambiguity discussed in the project design — even 
    the question-writer (in this case, guiding through the tutorial) can 
    unintentionally write an ambiguous prompt.



Q15: Is mahine new vs returning customers ka revenue split kya hai?
SOL: SELECT 
    CASE 
        WHEN c.signup_date >= date_trunc('month', current_date) THEN 'new'
        ELSE 'returning'
    END AS customer_type,
    SUM(o.total_amount) AS revenue
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.order_date >= date_trunc('month', current_date)
GROUP BY customer_type;


Q16: Kaun se customers ne session start kiya par kabhi order nahi kiya?
SOL: 
-> Option A — sirf NOT IN (simpler, LEFT JOIN hata do):

sql
select distinct s.customer_id
from sessions s
where s.customer_id not in (select customer_id from orders)
and s.customer_id is not null;

-> Option B — jo maine sikhaya tha, LEFT JOIN + IS NULL:

sql
select distinct s.customer_id
from sessions s
left join orders o on s.customer_id = o.customer_id
where o.id is null and s.customer_id is not null;



Q17: Monthly cancellation rate ka trend kya hai (pichle 6 mahine)?
SOL: SELECT date_trunc('month', order_date) AS month,
       COUNT(*) AS total_orders,
       COUNT(CASE WHEN status = 'cancelled' THEN 1 END) AS cancelled_orders
FROM orders
WHERE order_date >= date_trunc('month', current_date - interval '6 months')
  AND order_date < date_trunc('month', current_date)
GROUP BY month
ORDER BY month;



Q18: Is quarter ke top 5 products by revenue
SOL:
SELECT p.name, SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN orders o ON oi.order_id = o.id
WHERE o.order_date >= date_trunc('quarter', current_date)
GROUP BY p.name
ORDER BY revenue DESC
LIMIT 5;


Q19: Top 20% spenders jo 60+ din se order nahi kiye (high-value at-risk)
SOL:
WITH customer_spend AS (
    SELECT customer_id, SUM(total_amount) AS total_spend, MAX(order_date) AS last_order
    FROM orders
    GROUP BY customer_id
),
ranked AS (
    SELECT *, NTILE(5) OVER (ORDER BY total_spend DESC) AS spend_bucket
    FROM customer_spend
)
SELECT c.first_name, c.last_name, r.total_spend, r.last_order
FROM ranked r
JOIN customers c ON c.id = r.customer_id
WHERE r.spend_bucket = 1
  AND r.last_order < current_date - interval '60 days';


Q20: Test accounts exclude, is saal ka total valid revenue
SOL:
SELECT SUM(o.total_amount) AS total_revenue
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE c.is_test_account = FALSE
  AND o.status != 'refunded'
  AND o.order_date >= date_trunc('year', current_date)
  AND o.order_date < date_trunc('year', current_date) + interval '1 year';