#!/bin/sh
# Docker Compose - BEFORE (setiap container dijalankan manual)
# - Perintah panjang yang harus diketik ulang dan urutannya diingat sendiri
# - Setiap container ada di network default yang terpisah
# - localhost di dalam container API = container API itu sendiri, bukan PostgreSQL
# - API langsung jalan walaupun PostgreSQL belum siap
docker build -t demo-compose-api .

docker run -d --name demo-postgres -e POSTGRES_PASSWORD=app postgres:16-alpine
docker run -d --name demo-redis redis:7-alpine
docker run -d --name demo-api -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:app@localhost:5432/postgres \
  -e REDIS_URL=redis://localhost:6379/0 \
  demo-compose-api

sleep 5
curl -s localhost:8000/health/ready
