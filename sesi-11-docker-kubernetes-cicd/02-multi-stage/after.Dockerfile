# Multi-stage - AFTER
# Stage "builder": punya compiler, meng-install semua dependency ke /opt/venv
# Stage akhir   : hanya runtime (libpq5) + hasil install dari builder
# Compiler tidak ikut ke image akhir, jadi image lebih kecil dan celah keamanannya lebih sedikit.
FROM python:3.12-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY app ./app

RUN useradd --create-home appuser
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
