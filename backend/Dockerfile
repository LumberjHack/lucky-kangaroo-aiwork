# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (diagnostic + install propre)
COPY requirements.txt .
# 1) Afficher le contenu des requirements utilisés dans l'image
RUN echo "===== requirements.txt in image =====" \
    && sed -n '1,200p' requirements.txt \
    && echo "===== end requirements.txt ====="
# 2) Mettre à jour pip et installer sans cache ni --user
RUN python -V && pip -V \
    && pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip --version \
    && pip install --no-cache-dir -r requirements.txt \
    && pip check \
    && pip freeze | sort

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python environment from builder (global install)
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Command to run the application (note: wsgi exports `application`)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--worker-class", "gevent", "--timeout", "120", "wsgi:application"]
