FROM ghcr.io/alwatr/python:3.12.2

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 80

HEALTHCHECK CMD curl --fail http://localhost:80/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=80", "--server.address=0.0.0.0"]