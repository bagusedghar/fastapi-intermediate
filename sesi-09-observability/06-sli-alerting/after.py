"""SLI & Alerting - AFTER (alert dari SLI yang melewati SLO)

- SLI (Service Level Indicator): angka yang mengukur pengalaman user, dihitung dari metrics
    availability = request tidak 5xx / semua request
    latency      = request di bawah 300 ms / semua request
- SLO (Service Level Objective): target untuk SLI, misalnya availability >= 99.5%
- Alert hanya dikirim jika SLI di sebuah window berada di bawah SLO
Error sesekali di window normal tidak memicu alert. Window yang benar-benar bermasalah memicu 1 alert.
Di production, aturan ini ditulis sebagai alert rule Prometheus.

Jalankan: python after.py
"""

SLO = {"availability": 99.5, "latency": 95.0}      # persen


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


def sli(requests: list[dict]) -> dict:
    total = len(requests)
    ok = sum(r["status"] < 500 for r in requests)
    fast = sum(r["seconds"] < 0.3 for r in requests)
    return {"availability": ok / total * 100,
            "latency": fast / total * 100}


if __name__ == "__main__":
    alerts = 0
    for name, requests in WINDOWS.items():
        values = sli(requests)
        broken = [k for k, v in values.items() if v < SLO[k]]
        alerts += 1 if broken else 0
        status = f"ALERT: {', '.join(broken)}" if broken else "ok"
        print(f"{name}  availability={values['availability']:.1f}%"
              f"  latency<300ms={values['latency']:.1f}%  -> {status}")
    print(f"SLO: availability >= {SLO['availability']}%, "
          f"latency<300ms >= {SLO['latency']}%")
    print(f"Total alert ke tim on-call: {alerts}")
