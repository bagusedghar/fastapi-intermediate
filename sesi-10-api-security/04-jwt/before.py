"""JWT - BEFORE (token tanpa tanda tangan)

Setelah login, server memberi token berisi data user yang hanya di-encode base64.
Base64 bukan enkripsi dan tidak punya tanda tangan: siapa pun bisa membaca dan MENGUBAH isinya.
Budi mengganti role-nya menjadi "admin", dan server menerimanya. Token juga tidak pernah kedaluwarsa.

Jalankan: python before.py
"""
import base64
import json


def create_token(user: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(user).encode()).decode()


def read_token(token: str) -> dict:
    return json.loads(base64.urlsafe_b64decode(token))


if __name__ == "__main__":
    token = create_token({"sub": "budi@mail.com", "role": "customer"})
    print("Token dari server :", token)
    print("Isi token         :", read_token(token))

    # penyerang: decode, ganti role, encode lagi
    claims = read_token(token)
    claims["role"] = "admin"
    forged = create_token(claims)
    print("Token diubah      :", forged)
    print("Diterima server   :", read_token(forged))
