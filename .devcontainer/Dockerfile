FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*