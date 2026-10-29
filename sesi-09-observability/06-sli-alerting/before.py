"""SLI & Alerting - BEFORE (alert untuk setiap error, dashboard rata-rata)

Data: 3 window @ 5 menit, masing-masing 1000 request (simulasi).
Aturan alert: kirim alert setiap ada 1 request error.
- Di window normal pun ada error sesekali (client putus, timeout kecil), jadi alert terus berbunyi
- Tim on-call mulai mengabaikan alert
- Saat window 10:10 benar-benar bermasalah (banyak request lambat), alert-nya tenggelam di antara yang lain

Jalankan: python before.py
"""


def window(errors: int, slow: int, total: int = 1000) -> list[dict]:
    """Request simulasi: sebagian error, sebagian lambat (1.5 s)."""
    requests = []
    for i in range(total):
        requests.append({"status": 500 if i < errors else 200,
                         "seconds": 1.5 if i >= total - slow else 0.08})
    return requests


WINDOWS = {"10:00": window(errors=3, slow=20),
           "10:05": window(errors=2, slow=15),
           "10:10": window(errors=4, slow=150)}    # masalah

if __name__ == "__main__":
    alerts = 0
    for name, requests in WINDOWS.items():
        errors = sum(r["status"] >= 500 for r in requests)
        alerts += errors                       # 1 error = 1 alert
        avg = sum(r["seconds"] for r in requests) / len(requests)
        print(f"{name}  error={errors}  rata-rata={avg * 1000:.0f} ms"
              f"  -> {errors} alert")
    print(f"Total alert ke tim on-call: {alerts}")
