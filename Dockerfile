# Use official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create a directory for the application
RUN mkdir /app

# Set the working directory to /app
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
COPY requirements /app/requirements

RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Create a non-root user to run the application
RUN useradd -u 10001 -m summers && chown -R summers /app
USER summers

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "summers_api.asgi:application"]
