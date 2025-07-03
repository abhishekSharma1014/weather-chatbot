# Use slim Python base
FROM python:3.11-slim

# Set working directory
WORKDIR /app


# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install only pip dependencies (no system tools)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy only your app code
COPY . .

# Avoid copying large unnecessary files like .venv or __pycache__
RUN rm -rf /root/.cache /tmp/* .venv

EXPOSE 5000
CMD ["python", "app.py"]
