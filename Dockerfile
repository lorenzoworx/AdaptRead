FROM node:22-alpine AS frontend
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
RUN pip install --no-cache-dir .
COPY --from=frontend /build/frontend/dist ./frontend/dist
COPY artifacts/ ./artifacts/
RUN groupadd --system --gid 10001 adaptread \
    && useradd --system --uid 10001 --gid adaptread --no-create-home adaptread
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz')"
USER adaptread
CMD ["sh", "-c", "uvicorn adaptread.api.app:app --host 0.0.0.0 --port ${PORT}"]
