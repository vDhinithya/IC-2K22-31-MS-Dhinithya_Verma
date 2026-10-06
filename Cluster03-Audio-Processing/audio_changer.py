import requests
import json
# pyrefly: ignore [missing-import]
from IPython.display import Audio, display

# Setup & Configuration
ELEVENLABS_API_KEY = "YOUR_API_KEY"
VOICE_ID = "pNInz6obbf5AWiJ6oA3O" # Adam voice
INPUT_FILE_PATH = "input.mp3"
OUTPUT_FILE_PATH = "output.mp3"

url = f"https://api.elevenlabs.io/v1/speech-to-speech/{VOICE_ID}"
headers = {"xi-api-key": ELEVENLABS_API_KEY}

print(f"Preparing to send '{INPUT_FILE_PATH}' to ElevenLabs...")

try:
    # Read input audio and send API request
    with open(INPUT_FILE_PATH, 'rb') as audio_file:
        files = {'audio': (INPUT_FILE_PATH, audio_file, 'audio/mpeg')}
        data = {"model_id": "eleven_english_sts_v2"}
        response = requests.post(url, headers=headers, files=files, data=data)

    # Save output if successful
    if response.status_code == 200:
        with open(OUTPUT_FILE_PATH, 'wb') as output_file:
            output_file.write(response.content)
        
        print(f"Success! Saved to '{OUTPUT_FILE_PATH}'.")
        display(Audio(OUTPUT_FILE_PATH))
    else:
        print(f"Error {response.status_code}: {response.text}")

except FileNotFoundError:
    print(f"Error: '{INPUT_FILE_PATH}' not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
