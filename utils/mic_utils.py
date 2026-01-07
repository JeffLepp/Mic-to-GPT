import base64
import json
import asyncio
import queue

audio_q: "queue.Queue[bytes]" = queue.Queue(maxsize=200)

"""
Low-level audio + realtime stream utilities for the Listening GPT framework.

This module is responsible for:
- Capturing microphone audio (PCM16 @ 24 kHz)
- Buffering audio safely between threads
- Streaming audio frames to a Realtime WebSocket
- Receiving and printing model text output
- Enforcing client-side language gating (e.g., Russian-only handling)

This file contains NO application logic or instructions.
It acts as an infrastructure layer used by higher-level controllers
(e.g., listeningGPT.py).

Design notes:
- Audio callbacks must never block
- Queue is used to bridge the audio thread and asyncio loop
- Receiver only prints allowed output and ignores all other events
- Language filtering is enforced here to prevent unintended model responses

This module is reusable for other realtime listening tasks by
changing or removing the language filter.
"""

# Checks if message spoken contains russian
def contains_cyrillic(text: str) -> bool:
    for ch in text:
        if '\u0400' <= ch <= '\u04FF':
            return True
    return False

def audio_callback(indata, frames, time, status):
    if status:
        pass
    try:
        audio_q.put_nowait(bytes(indata))
    except queue.Full:
        pass


async def sender(ws):
    loop = asyncio.get_running_loop()
    while True:
        data = await loop.run_in_executor(None, audio_q.get)
        await ws.send(json.dumps({
            "type": "input_audio_buffer.append",
            "audio": base64.b64encode(data).decode("ascii"),
        }))


async def receiver(ws):
    partial = ""

    while True:
        event = json.loads(await ws.recv())
        etype = event.get("type")

        # ---- ONLY SHOW ENGLISH OUTPUT ----
        if etype in ("response.text.delta", "response.output_text.delta"):
            delta = event.get("delta", "")
            if delta:
                partial += delta
                print("\r" + partial, end="", flush=True)

        elif etype in ("response.text.done", "response.output_text.done"):
            print("\r" + partial.strip() + " " * 10, flush=True)
            partial = ""

        # If you wish to change this listening GPT to a different purpose, remove this check (checks for spoken russian)
        elif etype == "conversation.item.input_audio_transcription.completed":
            transcript = event.get("transcript", "")
            
            # HARD GATE
            if not contains_cyrillic(transcript):
                # Do NOTHING — no response created
                continue

        # ---- SILENTLY IGNORE EVERYTHING ELSE ----
        else:
            pass
