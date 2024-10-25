# Use the official Python image from Docker Hub
FROM python:3.10-slim

# Set environment variables to prevent Python from writing pyc files and to buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY package_requirements.txt .

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install the required Python packages
RUN pip install --no-cache-dir -r package_requirements.txt

# Copy the entire application code into the container
COPY . .

# Expose the port that the FastAPI app will run on
EXPOSE 8001

# Command to start the FastAPI application
CMD ["python", "app-public/app_public.py"]
