FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates tar \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .
RUN bash build.sh
RUN cd frontend && npm ci && npm run build

ENV ECHOCHESS_ENV=production
ENV ECHOCHESS_EPHEMERAL=true
ENV ECHOCHESS_COOKIE_SECURE=true
ENV ECHOCHESS_COOKIE_SAMESITE=lax
ENV STOCKFISH_PATH=/app/bin/stockfish

EXPOSE 8000
CMD python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
