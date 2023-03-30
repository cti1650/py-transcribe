import pyaudio
import wave
import docker

client = docker.from_env()
container = client.containers.get('py-transcribe-app-1')

p = pyaudio.PyAudio()
device_index = p.get_default_input_device_info()["index"]
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024, input_device_index=device_index)

while True:
    data = stream.read(1024)
    # Do something with the audio data