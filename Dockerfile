# Use Python slim image
FROM python:3.12-slim

# Create a non-root user and group for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    gcc \
    python3-dev \
    libpq-dev \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /home/appuser/app

# Upgrade pip and install build tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir --retries 10 --timeout 100 -r requirements.txt

# Copy the rest of the application source code
COPY . .

# Create required directories and set ownership
RUN mkdir -p uploads scraped_data && chown -R appuser:appuser .

# Copy and set entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to the non-root user
USER appuser

# Expose port 5000
EXPOSE 5000

# Command to run the application
ENTRYPOINT ["/entrypoint.sh"]
