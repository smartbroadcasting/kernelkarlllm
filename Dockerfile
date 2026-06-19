FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN set -eux; \
    find /etc/apt -type f \( -name "*.list" -o -name "*.sources" \) \
      -exec sed -i \
        -e 's|http://deb.debian.org|https://deb.debian.org|g' \
        -e 's|http://security.debian.org|https://security.debian.org|g' {} +; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      build-essential \
      cmake \
      ninja-build; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app.py .
COPY api ./api
COPY config ./config
COPY services ./services

RUN mkdir -p /models

EXPOSE 8100

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8100"]
