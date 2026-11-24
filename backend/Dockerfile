
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Install dependencies tanpa konfigurasi pip eksternal
RUN PIP_CONFIG_FILE=/dev/null pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
