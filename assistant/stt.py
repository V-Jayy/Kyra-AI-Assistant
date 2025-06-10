import asyncio
import queue
import threading
from typing import AsyncGenerator, Optional
import pyaudio


async def speech_chunks(mic_index: Optional[int] = None) -> AsyncGenerator[bytes, None]:
    """Asynchronously yield microphone audio chunks."""
    q: queue.Queue[bytes] = queue.Queue()

    def _worker() -> None:
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            input_device_index=mic_index,
            frames_per_buffer=8000,
        )
        stream.start_stream()
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            q.put(data)

    threading.Thread(target=_worker, daemon=True).start()
    loop = asyncio.get_running_loop()
    while True:
        data = await loop.run_in_executor(None, q.get)
        yield data
