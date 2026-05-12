FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project
COPY . .

# Install Python dependencies for ETL
RUN pip install --no-cache-dir -r etl/requirements.txt

# Create logs directory
RUN mkdir -p etl/logs

# Run the scheduler
CMD ["python", "-u", "etl/scheduler.py", "--interval", "1"]
