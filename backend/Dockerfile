# backend/Dockerfile

FROM python:3.10-slim

# 1) install OS dependencies for psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2) set workdir
WORKDIR /app

# 3) copy & install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) copy your app code
COPY . .

# 5) default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
