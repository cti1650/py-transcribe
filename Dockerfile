FROM python:3.7-slim-buster

RUN apt-get update && apt-get install -y git && \
    apt-get install -y alsa-utils && \
    apt-get install -y portaudio19-dev

COPY requirements.txt requirements.txt

RUN git clone https://github.com/awslabs/amazon-transcribe-streaming-sdk.git && \
    cd amazon-transcribe-streaming-sdk && \
    /usr/local/bin/python -m pip install --upgrade pip && \
    pip install -r requirements-dev.txt && \
    pip install -r /requirements.txt && \
    python setup.py install