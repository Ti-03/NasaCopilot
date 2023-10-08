from pyht import Client
from dotenv import load_dotenv
from pyht.client import TTSOptions
import os
load_dotenv()

client = Client(
    user_id=os.getenv("0FF6XfyvUMUzklEw7jxwCxol0Ww2"),
    api_key=os.getenv("4aff7233ea104407a9e87de3d867c789"),
)
options = TTSOptions(voice="s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json")
for chunk in client.tts("Can you tell me your account email or, ah your phone number?", options):
    # do something with the audio chunk
    print(type(chunk))