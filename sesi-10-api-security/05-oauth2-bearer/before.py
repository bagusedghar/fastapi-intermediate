"""OAuth2 Bearer - BEFORE (password disimpan apa adanya, "token" = email di URL)

- Password disimpan tanpa hash: jika database bocor, semua password langsung terbaca
- Setelah login, client cukup mengirim ?user=email. Siapa pun bisa mengaku sebagai user lain
- Email ikut tercatat di access log server dan history browser karena ada di URL

Jalankan: python before.py
"""
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

USERS = {"budi@mail.com": {"password": "budi12345", "role": "customer"},
         "ani@mail.com": {"password": "ani12345", "role": "customer"}}
app = FastAPI()


@app.post("/login")
def login(email: str, password: str):
    user = USERS.get(email)
    if user is None or user["password"] != password:
        raise HTTPException(401, "email atau password salah")
    return {"user": email}


@app.get("/me")
def me(user: str):
    return {"email": user, **USERS[user]}


if __name__ == "__main__":
    client = TestClient(app)
    print("Isi tabel users:", USERS)
    print("budi login ->", client.post(
        "/login", params={"email": "budi@mail.com",
                          "password": "budi12345"}).json())
    print("GET /me?user=ani@mail.com ->",
          client.get("/me", params={"user": "ani@mail.com"}).json())
