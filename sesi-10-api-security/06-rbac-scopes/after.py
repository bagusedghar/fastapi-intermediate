"""RBAC & Scopes - AFTER (hak akses dideklarasikan, dicek di satu tempat)

- RBAC (Role-Based Access Control): setiap role punya daftar izin (scope)
    customer -> orders:write
    admin    -> orders:write, products:write, reports:read
- Endpoint cukup menyatakan scope yang dibutuhkan lewat Security(current_user, scopes=[...])
- current_user menerima SecurityScopes dari FastAPI dan mengecek semuanya di satu tempat
Endpoint baru yang lupa menulis scope tetap butuh login, dan scope-nya terlihat jelas saat code review.

Jalankan: python after.py
"""
from fastapi import FastAPI, Header, HTTPException, Security
from fastapi.security import SecurityScopes
from fastapi.testclient import TestClient

USERS = {"budi@mail.com": "customer", "admin@toko.com": "admin"}
ROLE_SCOPES = {"customer": {"orders:write"},
               "admin": {"orders:write", "products:write",
                         "reports:read"}}
app = FastAPI()


def current_user(security_scopes: SecurityScopes,
                 x_user: str = Header()) -> dict:
    role = USERS[x_user]                            # anggap: dari JWT
    missing = set(security_scopes.scopes) - ROLE_SCOPES[role]
    if missing:
        raise HTTPException(403, f"butuh scope {sorted(missing)}")
    return {"sub": x_user, "role": role}


@app.post("/products")
def create_product(
        user: dict = Security(current_user, scopes=["products:write"])):
    return {"status": "created"}


@app.delete("/products/{product_id}")
def delete_product(
        product_id: int,
        user: dict = Security(current_user, scopes=["products:write"])):
    return {"status": "deleted"}


@app.get("/reports/sales")
def sales_report(
        user: dict = Security(current_user, scopes=["reports:read"])):
    return {"revenue": 12_500_000}


if __name__ == "__main__":
    client = TestClient(app)
    for user in ("budi@mail.com", "admin@toko.com"):
        for method, path in [("POST", "/products"),
                             ("DELETE", "/products/1"),
                             ("GET", "/reports/sales")]:
            response = client.request(method, path,
                                      headers={"X-User": user})
            print(f"{user.split('@')[0]:5} ({USERS[user]:8}) {method:6} "
                  f"{path:15} -> {response.status_code}")
