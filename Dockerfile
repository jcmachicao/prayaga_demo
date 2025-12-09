# Base image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port (optional, for Render)
EXPOSE 8000

# Entrypoint
CMD ["bash", "start.sh"]
# Or, if you skip start.sh:
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
