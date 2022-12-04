# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git gcc libz-dev \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

ENV PATH="${PATH}:/home/appuser/.local/bin"

# Install pip requirements
COPY requirements.txt .
COPY requirements ./requirements
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install -r requirements.txt

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "summers_api.asgi:application"]
