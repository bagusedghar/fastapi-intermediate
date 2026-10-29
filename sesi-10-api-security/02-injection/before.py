"""Injection - BEFORE (input user digabung langsung ke SQL)

Endpoint pencarian produk menyusun query dengan f-string.
Input user ikut menjadi bagian dari perintah SQL, jadi penyerang bisa menambah perintahnya sendiri:
UNION SELECT membaca tabel lain, termasuk email dan hash password user.

Jalankan: python before.py
"""
import sqlite3

from fastapi import FastAPI
from fastapi.testclient import TestClient

db = sqlite3.connect(":memory:", check_same_thread=False)
db.executescript("""
CREATE TABLE products (name TEXT, price INT);
INSERT INTO products VALUES ('Keyboard', 500000), ('Mouse', 100000);
CREATE TABLE users (email TEXT, password_hash TEXT);
INSERT INTO users VALUES ('admin@toko.com', '$argon2id$v=19$m=65536');
""")
app = FastAPI()


@app.get("/products/search")
def search(q: str):
    sql = f"SELECT name, price FROM products WHERE name LIKE '%{q}%'"
    return db.execute(sql).fetchall()


if __name__ == "__main__":
    client = TestClient(app)
    attack = "x' UNION SELECT email, password_hash FROM users --"
    for q in ["key", attack]:
        response = client.get("/products/search", params={"q": q})
        print(f"q = {q!r}\n  -> {response.json()}")
