# Start from a lightweight official Python image
FROM python:3.10-slim

# --- FIX: Install Docker CLI ---
# We need this so the container can run 'docker' commands
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    rm get-docker.sh && \
    apt-get clean
# --- End of Fix ---

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code (app.py, feedback.py, etc.)
COPY . .

# Expose the port that gunicorn will run on
EXPOSE 8080

# The command to run your application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]