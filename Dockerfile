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

# Expose Railway's dynamic PORT
# Railway sets PORT as environment variable at runtime
EXPOSE 8080

# Run the application using Railway's PORT environment variable
# Use $PORT directly (Railway always sets this at runtime)
# The WORKDIR is /app/backend, so Python can import main.app directly
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port $PORT"
