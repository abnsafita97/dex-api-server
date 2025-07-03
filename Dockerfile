# Use official Python image
FROM python:3.11-slim

# Install Java (OpenJDK 17)
RUN apt-get update && apt-get install -y openjdk-17-jre && apt-get clean

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Copy smali tools
COPY baksmali.jar /usr/local/bin/baksmali.jar
COPY smali.jar /usr/local/bin/smali.jar

# Expose port
EXPOSE 8080

# Run the app with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]