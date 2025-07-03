# Use an official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Copy baksmali and smali jars to a known location
COPY baksmali.jar /usr/local/bin/baksmali.jar
COPY smali.jar /usr/local/bin/smali.jar

# Expose the port
EXPOSE 8080

# Use gunicorn to run the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]