FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . /app/

# Create streamlit config directory and file
RUN mkdir -p /app/.streamlit
RUN echo "[server]\nheadless = true\naddress = \"0.0.0.0\"\nport = 5000" > /app/.streamlit/config.toml

# Make entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Set the entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]