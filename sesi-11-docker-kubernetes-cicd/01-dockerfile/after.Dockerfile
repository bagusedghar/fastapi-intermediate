# Dockerfile - AFTER
# - requirements.txt di-copy dan di-install DULU: selama tidak berubah,
#   layer pip install dipakai ulang dari cache
# - .dockerignore (after.Dockerfile.dockerignore) membuang secret dan file yang tidak perlu
# - Berjalan sebagai user biasa, tanpa --reload
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
