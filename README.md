# Running Instructions

Download requirements from requirements.txt

To run the listening GPT model, run 'activate.py'

## API Key

This project requires an OpenAI API key.

**Linux / macOS**
```bash
export OPENAI_API_KEY="your_api_key_here"
```


# Listening GPT Framework

Listening GPT is a small, cross-platform framework that connects your **microphone directly to a GPT model in real time**.

It continuously listens to audio input, streams it to a model, and displays the model’s output live in a terminal window.

The current example configuration is a **real-time Russian → English translator**, but the framework is designed to support many other listening-based use cases.



## What this project does

- Listens continuously to your microphone
- Streams audio to a GPT model in real time
- Detects when you finish speaking
- Processes speech through transcription and reasoning
- Displays text output instantly in the terminal

There is no push-to-talk and no audio files are saved.



## Requirements

- Python 3.9+
- A working microphone
- An OpenAI API key
- Internet connection

Supported operating systems:
- Linux
- macOS
- Windows


