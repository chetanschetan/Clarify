import psycopg
from dotenv import load_dotenv
import os
from faker import Faker
import random
from datetime import timedelta

load_dotenv()
conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
fake = Faker()

customer_ids = []

for _ in range(5000):
    cur.execute(
        "INSERT INTO customers (first_name, last_name, email, country, signup_date, is_test_account) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
        (fake.first_name(), fake.last_name(), fake.unique.email(), fake.country(), fake.date_between(start_date="-12M", end_date="today"), random.random()<0.01)
    )
    new_id = cur.fetchone()[0]
    customer_ids.append(new_id)

conn.commit()
print(f"{len(customer_ids)} customers inserted")



categories = ["Electronics", "Apparel", "Home", "Books", "Beauty"]
product_ids = []

for _ in range(200):
    cur.execute(
        "INSERT INTO products (name, category, price, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
        (fake.word().title()+" "+fake.word().title(), random.choice(categories), round(random.uniform(5,500),2), fake.date_between(start_date="-2y", end_date="-1M"))
    )
    new_id = cur.fetchone()[0]
    product_ids.append(new_id)

conn.commit()
print(f"{len(product_ids)} products inserted")




order_ids = []

for cid in customer_ids:
    n_orders = random.choices([0,1,2,3,5,8], weights=[15,30,25,15,10,5])[0]
    for _ in range(n_orders):
        cur.execute(
            "INSERT INTO orders (customer_id, order_date, status, total_amount) values (%s, %s, %s, %s) RETURNING id",
            (cid, fake.date_between(start_date="-12M", end_date="today"), random.choices(["completed", "cancelled", "refunded"], weights=[85, 8, 7])[0], 0) 
        )

        new_id = cur.fetchone()[0]
        order_ids.append(new_id)

conn.commit()
print(f"{len(order_ids)} orders inserted")



order_items = []
cur.execute("SELECT id, order_date, status FROM orders")
all_orders = cur.fetchall()

for order_id, order_date, status in all_orders:
    total = 0
    n_items = random.randint(1,4)
    for _ in range(n_items):
        pid = random.choice(product_ids)
        cur.execute("SELECT price FROM products WHERE id = %s", (pid,))
        price = cur.fetchone()[0]
        qty = random.randint(1, 3)

        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s) RETURNING id",
            (order_id, pid, qty, price)
        )

        total += price * qty

        new_id = cur.fetchone()[0]
        order_items.append(new_id)

    if status == 'refunded':
        refund_date = order_date + timedelta(days=random.randint(1,10))
        cur.execute(
            "INSERT INTO refunds (order_id, refund_date, amount, reason) VALUES (%s, %s, %s, %s)",
            (order_id, refund_date, total, "customer request")
        )
    cur.execute("UPDATE orders SET total_amount = %s WHERE id = %s", (total, order_id))

conn.commit()
print(f"{len(order_items)} order items inserted")



devices = ["mobile", "desktop", "tablet"]

for _ in range(1000):
    start = fake.date_time_between(start_date='-12M', end_date='now')
    end = start + timedelta(minutes=random.randint(1,45))

    if random.random() < 0.2:
        cid = None
    else:
        cid = random.choice(customer_ids)

    cur.execute(
        "INSERT INTO sessions (customer_id, session_start, session_end, device) VALUES (%s, %s, %s, %s)",
        (cid, start, end, random.choice(devices))
    )

conn.commit()
print(f"sessions inserted")