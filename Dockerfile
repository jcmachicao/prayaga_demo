FROM python:3.10-slim

# Create working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Render port for HTTP
ENV PORT=7860
EXPOSE 7860

# Start the service
CMD ["bash", "start.sh"]
 
