# Dockerfile - BEFORE
# Masalahnya:
# - COPY . . di awal: kode berubah sedikit, pip install diulang dari nol
# - Semua file ikut masuk image, termasuk .env.local berisi secret
# - Berjalan sebagai root, dan --reload (mode development)
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]
