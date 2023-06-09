FROM python:3.7-slim-buster

EXPOSE 3000

RUN apt-get update && apt-get install -y git && \
    apt-get install -y alsa-utils && \
    apt-get install -y build-essential && \
    apt-get install -y portaudio19-dev

COPY requirements.txt requirements.txt

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN git clone https://github.com/awslabs/amazon-transcribe-streaming-sdk.git && \
    cd amazon-transcribe-streaming-sdk && \
    /usr/local/bin/python -m pip install --upgrade pip && \
    pip install -r requirements-dev.txt && \
    pip install -r /requirements.txt && \
    python setup.py install && \
    curl -fsSL https://get.deta.dev/cli.sh | sh

# ENTRYPOINT ["uvicorn", "amazon-transcribe-streaming-sdk.src.main:app", "--host", "0.0.0.0","--port", "3000", "--reload"]