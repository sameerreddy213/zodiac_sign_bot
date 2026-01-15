# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for Pillow and other potential libraries
# (libgl1-mesa-glx might be needed for some image ops, but keeping it minimal first)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY horoscope_bot/requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Define environment variable for assets (optional, as defaults work)
ENV ASSETS_DIR=/app

# Run main.py when the container launches
CMD ["python", "horoscope_bot/main.py"]
