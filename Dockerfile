FROM python:3.7-slim-buster

RUN apt-get update && apt-get install -y git

COPY requirements.txt requirements.txt

RUN git clone https://github.com/awslabs/amazon-transcribe-streaming-sdk.git && \
    cd amazon-transcribe-streaming-sdk && \
    pip install -r requirements-dev.txt && \
    pip install -r /requirements.txt && \
    python setup.py install