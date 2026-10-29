"""OAuth2 Bearer - AFTER (password di-hash, login menghasilkan JWT, dikirim di header)

- Password disimpan sebagai hash Argon2 (pwdlib). Hash tidak bisa dibalik jadi password
- POST /token menerima form username + password (format OAuth2 password flow), lalu memberi JWT
- Endpoint terproteksi membaca header Authorization: Bearer <token> lewat OAuth2PasswordBearer
- Token salah, kedaluwarsa, atau tidak ada: 401 dengan header WWW-Authenticate: Bearer
Swagger UI (/docs) otomatis punya tombol Authorize untuk login.

Jalankan: python after.py
"""
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import (OAuth2PasswordBearer,
                              OAuth2PasswordRequestForm)
from fastapi.testclient import TestClient
from pwdlib import PasswordHash

SECRET = "ganti-dengan-secret-panjang-dari-env"   # contoh 07
hasher = PasswordHash.recommended()               # Argon2
USERS = {"budi@mail.com": {"password_hash": hasher.hash("budi12345"),
                           "role": "customer"},
         "ani@mail.com": {"password_hash": hasher.hash("ani12345"),
                          "role": "customer"}}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
app = FastAPI()
UNAUTHORIZED = HTTPException(401, "token tidak valid",
                             headers={"WWW-Authenticate": "Bearer"})


@app.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = USERS.get(form.username)
    if user is None or not hasher.verify(form.password,
                                         user["password_hash"]):
        raise HTTPException(401, "email atau password salah")
    exp = datetime.now(timezone.utc) + timedelta(minutes=30)
    token = jwt.encode({"sub": form.username, "role": user["role"],
                        "exp": exp}, SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


def current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise UNAUTHORIZED


@app.get("/me")
def me(user: dict = Depends(current_user)):
    return {"email": user["sub"], "role": user["role"]}


if __name__ == "__main__":
    client = TestClient(app)
    stored = USERS["budi@mail.com"]["password_hash"]
    print("Isi tabel users (budi):", stored[:45] + "...")
    wrong = client.post("/token", data={"username": "budi@mail.com",
                                        "password": "salah"})
    print("Login password salah ->", wrong.status_code)
    login = client.post("/token", data={"username": "budi@mail.com",
                                        "password": "budi12345"})
    token = login.json()["access_token"]
    print("Login benar ->", login.status_code, token[:30] + "...")
    auth = {"Authorization": f"Bearer {token}"}
    print("GET /me + Bearer ->", client.get("/me", headers=auth).json())
    no_token = client.get("/me")
    print("GET /me tanpa token ->", no_token.status_code,
          no_token.headers["www-authenticate"])
