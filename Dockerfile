# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY setup.py .
COPY src/ src/
RUN pip install --upgrade pip
RUN pip install .

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Copy scripts and data
COPY scripts/ scripts/
COPY data/ data/
COPY .env .

# Set environment variables for encryption
ENV AES_KEY=${AES_KEY}
ENV AES_IV=${AES_IV}

# Expose ports if necessary (optional)
# EXPOSE 8000

# Define the default command to run the application
CMD ["python", "src/quiznexusai/main.py"]
