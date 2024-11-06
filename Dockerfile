# Dockerfile
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

