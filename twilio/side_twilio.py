from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

import requests
import time
import openai
import os
from dotenv import load_dotenv

# Load the variables from the .env file
load_dotenv()

# Set up Twilio client
account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
recipient_phone_number = os.getenv('RECIPIENT_PHONE_NUMBER')
hume_api_key = os.getenv('HUME_API_KEY')

client = Client(account_sid, auth_token)

# Set up OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Function to generate response using OpenAI
def generate_response(prompt):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=50,
        temperature=0.7,
        n=1,
        stop=None
    )
    return response.choices[0].text.strip()

# Function to handle incoming call
def handle_incoming_call():
    response = VoiceResponse()
    response.say("Hello, how can I assist you?")
    response.record(max_length=30, action='/process_recording')
    return str(response)

def convert_speech_to_text(recording_url):
    url = "https://api.hume.ai/v0/batch/jobs"

    payload = "{\"models\":{\"face\":{\"fps_pred\":3,\"prob_threshold\":0.99,\"identify_faces\":false,\"min_face_size\":60,\"save_faces\":false},\"prosody\":{\"granularity\":\"utterance\",\"identify_speakers\":false,\"window\":{\"length\":4,\"step\":1}},\"language\":{\"granularity\":\"word\",\"identify_speakers\":false},\"ner\":{\"identify_speakers\":false}},\"transcription\":{\"language\":null},\"notify\":false}"
    headers = {
        "accept": "application/json; charset=utf-8",
        "content-type": "application/json; charset=utf-8",
        "X-Hume-Api-Key": hume_api_key
    }

    response = requests.post(url, data=payload, headers=headers)

    print(response.text)

# Function to process the recording and generate a response
def process_recording(recording_url):
    # Convert recording to text using speech-to-text API or library
    # Here, let's assume we have a function called `convert_speech_to_text` for this purpose
    recipient_message = convert_speech_to_text(recording_url)

    # Generate a response using OpenAI
    prompt = "Recipient said: " + recipient_message
    generated_response = generate_response(prompt)

    # Save the generated response as an audio file
    audio_filename = 'generated_response.mp3'
    save_generated_response_as_audio(generated_response, audio_filename)

    # Respond to the recipient with the generated answer
    response = VoiceResponse()
    response.play(audio_filename)
    response.record(max_length=30, action='/process_recording')
    return str(response)

# Function to save the generated response as an audio file
def save_generated_response_as_audio(generated_response, filename):
    # Convert the generated response to audio and save it as the specified filename
    # Here, you will need to use a suitable text-to-speech library or service to convert the text to audio
    # Ensure that the audio file is saved with the .mp3 extension

    # Example code using the pyttsx3 library
    import pyttsx3
    engine = pyttsx3.init()
    engine.save_to_file(generated_response, filename)
    engine.runAndWait()

# Create a Twilio call
call = client.calls.create(
    twiml=handle_incoming_call(),
    to=recipient_phone_number,
    from_=twilio_phone_number
)

# Twilio webhook to process the recording and generate a response
@app.route('/process_recording', methods=['POST'])
def process_recording_webhook():
    recording_url = request.form['RecordingUrl']
    response = process_recording(recording_url)
    return response

# Start the Flask server to listen for incoming requests
if __name__ == '__main__':
    app.run()
