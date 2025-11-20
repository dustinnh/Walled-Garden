FROM python:3.11-slim

WORKDIR /app

# Install dig (bind9-dnsutils package)
RUN apt-get update &&     apt-get install -y bind9-dnsutils &&     rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5001

# Use Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "60", "app:app"]
