# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        nodejs \
        npm \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy pyproject.toml, uv.lock, and README.md first for better caching
COPY pyproject.toml uv.lock README.md ./

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Copy the rest of the application's code into the container
COPY . .

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Create staticfiles directory and set permissions
RUN mkdir -p /app/staticfiles && chmod 755 /app/staticfiles

# Build CSS
WORKDIR /app/theme/static_src
RUN npm install && npm run build

# Switch back to app directory
WORKDIR /app

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser
