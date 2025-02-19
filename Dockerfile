# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    libportaudiocpp0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make the audio directory
RUN mkdir -p /app/audio

# Expose the port the app runs on
EXPOSE 5000

# Define environment variable
ENV AUDIO_DIR=/app/audio

# Run the application
CMD ["gunicorn", "app:app"]