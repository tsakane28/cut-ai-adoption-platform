FROM python:3.11-slim

WORKDIR /app

# Copy requirements file
COPY pyproject.toml uv.lock /app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uv && \
    uv pip install --no-cache-dir -e .

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