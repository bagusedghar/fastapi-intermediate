"""Aplikasi kecil untuk contoh Dockerfile. Isinya sengaja sederhana, yang dibahas adalah image-nya."""
from fastapi import FastAPI

app = FastAPI()


@app.get("/health/live")
def live():
    return {"status": "ok"}
