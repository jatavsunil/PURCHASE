# Use lightweight Python base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for MySQL and build tools
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the project files
COPY . .

# Expose the port Flask will run on
EXPOSE 8080

# Start the Flask app using Waitress (production-ready WSGI)
CMD ["waitress-serve", "--host=0.0.0.0", "--port=8080", "app:app"]
