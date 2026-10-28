"""Cache-Aside - BEFORE

Setiap request detail produk selalu query ke database.
Anggap query-nya berat (join, hitung rating, dll) dan butuh 0.5 detik.
Produk yang sama dibuka 5 kali = 5 query dengan hasil yang sama persis.

Jalankan demo: python before.py
"""
import time

PRODUCTS = {1: {"id": 1, "name": "Keyboard", "price": 500_000}}
db_queries = 0


def query_product(product_id: int) -> dict:
    global db_queries
    db_queries += 1
    time.sleep(0.5)               # anggap: query berat
    return dict(PRODUCTS[product_id])


def get_product(product_id: int) -> dict:
    return query_product(product_id)


if __name__ == "__main__":
    start = time.perf_counter()
    for _ in range(5):
        get_product(1)
    took = time.perf_counter() - start
    print(f"5 request: {took:.1f} detik, "
          f"query ke database: {db_queries}")    # 2.5 detik, 5
