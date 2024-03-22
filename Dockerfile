FROM ghcr.io/alwatr/python:3.12.2

WORKDIR /app

RUN apk add --no-cache \
    ffmpeg \
    gcc \
    g++ \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    make \
    cmake

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 80

HEALTHCHECK CMD curl --fail http://localhost:80/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=80", "--server.address=0.0.0.0"]