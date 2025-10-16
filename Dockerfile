# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy backend directory
COPY backend/ /app/backend/

# Set working directory to backend
WORKDIR /app/backend

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose Railway's dynamic PORT (defaults to 8000 for local dev)
ARG PORT=8000
EXPOSE ${PORT}

# Run the application using Railway's PORT environment variable
# Using shell form to enable variable substitution at runtime
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
