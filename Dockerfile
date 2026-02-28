# Use the official Microsoft Playwright image which contains all necessary Chromium system dependencies natively
FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

# Install system dependencies required for Telugu font shaping
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-telu \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY horoscope_bot/requirements.txt /app/requirements.txt

# Install python packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Force Playwright to download Chromium explicitly (safe fallback)
RUN playwright install chromium

# Copy the current directory contents into the container at /app
COPY . /app

# Define environment variables
ENV ASSETS_DIR=/app/assets
ENV PYTHONUNBUFFERED=1

# Run main.py when the container launches
CMD ["python", "horoscope_bot/main.py"]
