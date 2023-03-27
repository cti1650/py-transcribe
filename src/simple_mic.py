import asyncio
import subprocess
import sys
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent


class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                print(alt.transcript)


def mic_stream():
    proc = subprocess.Popen(
        ["arecord", "-f", "S16_LE", "-r", "16000", "-c", "1", "-t", "raw"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
    )
    print("start mic_stream")
    while True:
        data = proc.stdout.read(1024 * 2)
        if not data:
            break
        yield data

    print("end mic_stream")

    proc.terminate()
    proc.wait()


async def write_chunks(stream):
    for chunk in mic_stream():
        await stream.input_stream.send_audio_event(audio_chunk=chunk)
    await stream.input_stream.end_stream()


async def basic_transcribe():
    print("start basic_transcribe")
    client = TranscribeStreamingClient(region="us-west-2")

    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=16000,
        media_encoding="pcm",
    )

    handler = MyEventHandler(stream.output_stream)
    await asyncio.gather(write_chunks(stream), handler.handle_events())


loop = asyncio.get_event_loop()
loop.run_until_complete(basic_transcribe())
loop.close()
