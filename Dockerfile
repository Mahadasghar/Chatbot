# Use Python slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Create required directories
RUN mkdir -p /app/uploads \
    /app/scraped_data

# Upgrade pip and install build tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements and package-lock first (for better caching)
COPY requirements.txt .

# Install Python packages
RUN  pip install --no-cache-dir --retries 10 --timeout 100 -r requirements.txt 

# Copy application files
COPY app.py .
COPY brain.py .
COPY scrapy.cfg .
COPY package-lock.json .
COPY file.json .
COPY utils/ ./utils/
COPY static/ ./static/
COPY templates/ ./templates/
COPY scraped_data/ ./scraped_data/
COPY gas_furnaces/ ./gas_furnaces/

# Copy and set entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port 5000
EXPOSE 5000

# Command to run the application
ENTRYPOINT ["/entrypoint.sh"]
