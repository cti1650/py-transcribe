import asyncio
import json
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Transcribe WebSocket</title>
    </head>
    <body>
        <h1>Transcribe WebSocket</h1>
        <form>
            <input type="text" id="transcript" size="50" readonly>
        </form>
        <script>
            var ws = new WebSocket("ws://localhost:5500/ws");
            var transcript = document.getElementById("transcript");
            ws.onmessage = function(event) {
                var data = JSON.parse(event.data);
                transcript.value += data.transcript + "\\n";
            };
        </script>
    </body>
</html>
"""

class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                transcript = alt.transcript
                await websocket.send_text(json.dumps({"transcript": transcript}))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client = TranscribeStreamingClient(region="us-west-2")
    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=16000,
        media_encoding="pcm",
    )
    handler = MyEventHandler(stream.output_stream)
    asyncio.create_task(write_chunks(stream, websocket))
    await handler.handle_events()

async def write_chunks(stream, websocket):
    async for chunk, status in mic_stream():
        await stream.input_stream.send_audio_event(audio_chunk=chunk)
    await stream.input_stream.end_stream()

async def mic_stream():
    loop = asyncio.get_event_loop()
    input_queue = asyncio.Queue()

    def callback(indata, frame_count, time_info, status):
        loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

    stream = sounddevice.RawInputStream(
        channels=1,
        samplerate=16000,
        callback=callback,
        blocksize=1024 * 2,
        dtype="int16",
    )
    with stream:
        while True:
            indata, status = await input_queue.get()
            yield indata, status

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.get("/app")
async def get():
    return {"test":"ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000)