# syntax=docker/dockerfile:1

FROM golang:1.22-bullseye AS builder
WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o vector-launcher ./

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=builder /app/vector-launcher ./vector-launcher
COPY add_documents.py add_documents_bdd_tests.py bdd_tests.feature ./

ENV CHROMA_DB_DIR=/app/db
VOLUME ["/app/db"]

ENTRYPOINT ["./vector-launcher"]
