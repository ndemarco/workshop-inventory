# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && find /usr/local/lib/python3.11 -type d -name '__pycache__' -exec rm -rf {} + \
    && find /usr/local/lib/python3.11 -type f -name '*.pyc' -delete

# Runtime stage - distroless
FROM gcr.io/distroless/python3-debian12

WORKDIR /app

# Copy Python runtime and installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/lib/x86_64-linux-gnu/libpq* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libssl* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libcrypto* /usr/lib/x86_64-linux-gnu/

# Copy application code
COPY app/ ./app/
COPY run.py .

# Expose port
EXPOSE 5000

# Set Python path
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages
ENV PYTHONUNBUFFERED=1

# Run as non-root (distroless uses nonroot user by default)
USER nonroot

# Run Python - distroless has python3 in PATH
ENTRYPOINT ["python3"]
CMD ["-u", "run.py"]
