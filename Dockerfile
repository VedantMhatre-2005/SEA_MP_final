# ─────────────────────────────────────────────────────────────────────────────
# ASPRAMS Dockerfile
# Multi-stage build: builds the Vite frontend, then serves everything via
# the FastAPI backend using Uvicorn.
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Build Frontend ───────────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Install dependencies first (cache layer)
COPY frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY frontend/ ./
ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build
# Built files are in /app/frontend/dist/

# ── Stage 2: Python Backend ───────────────────────────────────────────────────
FROM python:3.11-slim AS backend

WORKDIR /app

# Install Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend into backend's static directory
COPY --from=frontend-builder /app/frontend/dist ./backend/static/

# ── Runtime Config ────────────────────────────────────────────────────────────
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Run Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
