# Image aplikasi demo untuk contoh 04-06.
# Build: docker build -t k8s-demo:1.0 k8s-demo-app
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install --no-cache-dir "fastapi>=0.115,<1.0" "uvicorn[standard]>=0.30"
COPY main.py .

RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
