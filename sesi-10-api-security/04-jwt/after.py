"""JWT - AFTER (token ditandatangani server dan punya masa berlaku)

JWT terdiri dari tiga bagian: header.payload.signature
- payload berisi claims: sub (siapa), role, scope, exp (kapan kedaluwarsa)
- signature dihitung dari header + payload memakai SECRET yang hanya diketahui server (HS256)
Payload tetap bisa dibaca siapa pun, jadi jangan menyimpan data rahasia di dalamnya.
Tetapi payload yang diubah membuat signature tidak cocok, dan token ditolak.

Jalankan: python after.py
"""
import base64
import json
from datetime import datetime, timedelta, timezone

import jwt

SECRET = "ganti-dengan-secret-panjang-dari-env"   # contoh 07


def create_token(sub: str, role: str, minutes: int = 30) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    claims = {"sub": sub, "role": role, "exp": exp}
    return jwt.encode(claims, SECRET, algorithm="HS256")


def read_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=["HS256"])


def forge(token: str) -> str:
    """Penyerang: ubah role di payload, signature tetap yang lama."""
    header, payload, signature = token.split(".")
    claims = json.loads(base64.urlsafe_b64decode(payload + "=="))
    claims["role"] = "admin"
    payload = base64.urlsafe_b64encode(
        json.dumps(claims).encode()).decode().rstrip("=")
    return f"{header}.{payload}.{signature}"


if __name__ == "__main__":
    token = create_token("budi@mail.com", "customer")
    print("Token dari server :", token[:60] + "...")
    print("Isi token         :", read_token(token))
    expired = create_token("budi@mail.com", "customer", minutes=-1)
    for name, attempt in [("Token diubah", forge(token)),
                          ("Token kedaluwarsa", expired)]:
        try:
            read_token(attempt)
        except jwt.InvalidTokenError as exc:
            print(f"{name:<18}: ditolak, {type(exc).__name__}")
