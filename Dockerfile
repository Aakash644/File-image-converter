# syntax=docker/dockerfile:1

# Set the base image with a specific Python version
ARG PYTHON_VERSION=3.11.9
FROM python:${PYTHON_VERSION}-slim as base

# Prevent Python from writing .pyc files and from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Create a non-privileged user that the app will run under
ARG UID=10001
RUN adduser --disabled-password --gecos "" --home "/nonexistent" --shell "/sbin/nologin" --no-create-home --uid "${UID}" appuser

# Download dependencies
# Utilize Docker cache to speed up builds by leveraging the cache mount for pip
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Create necessary directories and set permissions
RUN mkdir -p /app/uploads /app/downloads && \
    chown -R appuser:appuser /app/uploads /app/downloads

# Switch to the non-privileged user to run the application
USER appuser

# Copy the source code into the container
COPY . .

# Ensure the application binds to all interfaces (0.0.0.0)
# and expose the port it will run on
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
