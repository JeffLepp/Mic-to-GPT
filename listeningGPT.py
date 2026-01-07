import os
import json
import asyncio

import sounddevice as sd
import websockets

from utils.mic_utils import receiver, sender, audio_callback, audio_q

"""
This script configures and runs a realtime Listening GPT instance,
currently specialized as a Russian → English interpreter.

Architecture:
- All audio I/O and streaming logic lives in utils/mic_utils.py
- This file contains ONLY orchestration and configuration
- No language logic or audio buffering is implemented here

Current mode:
- Listens continuously to microphone input
- Detects spoken Russian
- Outputs English translation only
- Produces no output for non-Russian speech

This file can be adapted to other realtime listening tasks
If you wish to change functionality, remove check on line 78 in mic_utils. 
"""

WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-realtime-mini-2025-12-15"

SAMPLE_RATE = 24000
CHANNELS = 1
DTYPE = "int16"

FRAME_MS = 20
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)

# A note about prompting:

# When designing models for very specific tasks such as realtime translation
# lengthy and complex instructions can cause more issues when solving for
# unexpected behavior. 
# 
# While complex prompting techniques can offer many examples and rules for
# a model, the best set of instructions for the translator is seen below.

INSTRUCTIONS = (
    "You are a real-time interpreter. " 
    "The user speaks Russian. Output ONLY the English translation. " 
    "No extra commentary, no quotes, no prefixes."
)

async def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set") 

    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1",
    }

    async with websockets.connect(
        WS_URL,
        additional_headers=headers,
        max_size=2**24,
    ) as ws:

        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["text"],
                "instructions": INSTRUCTIONS,
                "input_audio_format": "pcm16", 
                "input_audio_transcription": {
                    "model": "gpt-4o-mini-transcribe",
                    "language": "ru"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.65,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500,
                    "create_response": True,
                    "interrupt_response": True
                }
            }
        }))

        with sd.RawInputStream(
            samplerate=SAMPLE_RATE, 
            blocksize=FRAME_SAMPLES,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=audio_callback,
        ):
            await asyncio.gather(sender(ws), receiver(ws))


if __name__ == "__main__": 
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
