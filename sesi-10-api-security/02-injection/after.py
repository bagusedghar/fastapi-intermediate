"""Injection - AFTER (parameter query)

Query ditulis dengan placeholder (?), lalu nilai dari user dikirim terpisah.
Database memperlakukan nilai itu sebagai DATA, bukan bagian dari perintah SQL.
Input penyerang hanya dicari sebagai teks biasa, dan tidak ada produk dengan nama seperti itu.
SQLAlchemy (select(...).where(...) dan text(...) dengan :param) memakai cara yang sama.

Jalankan: python after.py
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
    sql = "SELECT name, price FROM products WHERE name LIKE ?"
    return db.execute(sql, (f"%{q}%",)).fetchall()


if __name__ == "__main__":
    client = TestClient(app)
    attack = "x' UNION SELECT email, password_hash FROM users --"
    for q in ["key", attack]:
        response = client.get("/products/search", params={"q": q})
        print(f"q = {q!r}\n  -> {response.json()}")
