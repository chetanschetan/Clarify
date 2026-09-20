CREATE TABLE customers (
    id              SERIAL PRIMARY KEY,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    email           TEXT UNIQUE NOT NULL,
    country         TEXT NOT NULL,
    signup_date     DATE NOT NULL,
    is_test_account BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    price       NUMERIC(10,2) NOT NULL,
    created_at  DATE NOT NULL
);

CREATE TABLE orders (
    id            SERIAL PRIMARY KEY,
    customer_id   INTEGER NOT NULL REFERENCES customers(id),
    order_date    DATE NOT NULL,
    status        TEXT NOT NULL CHECK (status IN ('completed','cancelled','refunded')),
    total_amount  NUMERIC(10,2) NOT NULL
);

CREATE TABLE order_items (
    id          SERIAL PRIMARY KEY,
    order_id    INTEGER NOT NULL REFERENCES orders(id),
    product_id  INTEGER NOT NULL REFERENCES products(id),
    quantity    INTEGER NOT NULL,
    unit_price  NUMERIC(10,2) NOT NULL
);

CREATE TABLE refunds (
    id           SERIAL PRIMARY KEY,
    order_id     INTEGER NOT NULL REFERENCES orders(id),
    refund_date  DATE NOT NULL,
    amount       NUMERIC(10,2) NOT NULL,
    reason       TEXT
);

CREATE TABLE sessions (
    id             SERIAL PRIMARY KEY,
    customer_id    INTEGER REFERENCES customers(id),
    session_start  TIMESTAMP NOT NULL,
    session_end    TIMESTAMP,
    device         TEXT
);