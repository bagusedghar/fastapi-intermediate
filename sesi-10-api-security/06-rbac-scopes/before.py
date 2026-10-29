"""RBAC & Scopes - BEFORE (cek role ditulis manual di setiap endpoint)

Setiap endpoint admin menulis sendiri: if user["role"] != "admin": raise 403.
Pengecekan tersebar dan mudah terlupa. Di sini DELETE /products/{id} lupa dicek,
jadi customer bisa menghapus produk.

Jalankan: python before.py
"""
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

USERS = {"budi@mail.com": "customer", "admin@toko.com": "admin"}
app = FastAPI()


def current_user(x_user: str = Header()) -> dict:
    return {"sub": x_user, "role": USERS[x_user]}   # anggap: dari JWT


@app.post("/products")
def create_product(user: dict = Depends(current_user)):
    if user["role"] != "admin":
        raise HTTPException(403, "khusus admin")
    return {"status": "created"}


@app.delete("/products/{product_id}")
def delete_product(product_id: int,
                   user: dict = Depends(current_user)):
    return {"status": "deleted"}             # lupa cek role


@app.get("/reports/sales")
def sales_report(user: dict = Depends(current_user)):
    if user["role"] != "admin":
        raise HTTPException(403, "khusus admin")
    return {"revenue": 12_500_000}


if __name__ == "__main__":
    client = TestClient(app)
    budi = {"X-User": "budi@mail.com"}
    for method, path in [("POST", "/products"), ("DELETE", "/products/1"),
                         ("GET", "/reports/sales")]:
        response = client.request(method, path, headers=budi)
        print(f"budi (customer) {method:6} {path:15} -> "
              f"{response.status_code}")
