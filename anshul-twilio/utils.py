import openai
import requests
import uuid
import configs

# utils
def voice_to_text(url):
    # Download the file from `url` and save it locally under `file_name`:
    openai.api_key = configs.openai
    random_uuid = str(uuid.uuid4())
    try:
        
        file_name = random_uuid + ".mp3"
        response = requests.get(url)
        with open(file_name, 'wb') as f:
            f.write(response.content)
        
        # Transcribe the audio file
        with open(file_name, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        
        return transcript['text']
    except:
        return ""