FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port
EXPOSE 5000

# Environment variables
ENV PORT=5000
ENV DEBUG=False

# Run the application
CMD ["python", "app.py"]