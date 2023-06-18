import json
import requests
import boto3
import requests
import os, sys
from dotenv import load_dotenv

import openai

sys.path.append('../')  # Add the parent directory to the system path
from chat import Interaction

interaction = Interaction(task="create a new account", context_directory="./")
interaction.recipient = "People's Gas"

load_dotenv()

# access-key= MICPMAWAWF2KI1CRWU0B
# secret-key= DkLNyYz0uP1EJINhAizYIlRLzAgWMZSHzbH11RZY

""" Functions to help out with saving to wasabi/file uploads.
    upload_file_to_wasabi --> Upload mp3 file to wasabi
    get_url_recording --> Download mp3 file from url
    count_files_in_directory --> Count number of files in a directory, to set the name of the new file name.
"""

def upload_file_to_wasabi(file_path, bucket_name):
    s3 = boto3.client('s3',
                      endpoint_url='https://s3.us-west-1.wasabisys.com',  # Use the correct endpoint URL for your Wasabi region
                      aws_access_key_id='6UQ6BKLP89DNA5G37191',  # Replace with your access key
                      aws_secret_access_key='tpkQAodRS6LfjfC33VTF8GzhorewzhzfWuElr8sI')  # Replace with your secret key

    file_name = os.path.basename(file_path)

    try:
        s3.upload_file(file_path, bucket_name, file_name)
        print(f"File uploaded to Wasabi successfully!")
    except Exception as e:
        print("Something went wrong: ", e)


def get_url_recording(url):
    response = requests.get(url, stream=True)
    print("creating a response")

    # Ensure the request is successful
    if response.status_code == 200:
        # Open the file in write-binary mode and write the response content to it
        with open('output.mp3', 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
    else:
        print('Failed to download the file.')



def count_files_in_directory(directory):
    return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])

""" Functions to help out with Humes API calls for speech to text."""
def convert_speech_to_text(recording_url):
    return convert_speech_to_text_whisper(recording_url)
    
def convert_speech_to_text_whisper(recording_url):
    # Download the audio file from the URL
    response = requests.get(recording_url)
    print(recording_url)
    audio_file = response.content

    # Save the audio data to a file
    with open("temp.wav", "wb") as file:
        file.write(audio_file)

    # Transcribe the audio using Whisper API
    with open("temp.wav", "rb") as file:
        transcript = openai.Audio.transcribe("whisper-1", file)
    
    return transcript.text
    
def convert_speech_to_text_hume(recording_url):
    url = "https://api.hume.ai/v0/batch/jobs"

    payload = "{\"models\":{\"face\":{\"fps_pred\":3,\"prob_threshold\":0.99,\"identify_faces\":false,\"min_face_size\":60,\"save_faces\":false},\"prosody\":{\"granularity\":\"utterance\",\"identify_speakers\":false,\"window\":{\"length\":4,\"step\":1}},\"language\":{\"granularity\":\"word\",\"identify_speakers\":false},\"ner\":{\"identify_speakers\":false}},\"transcription\":{\"language\":null}," + "\"urls\":[\"" + recording_url + "\"],\"notify\":false}"
    headers = {
        "accept": "application/json; charset=utf-8",
        "content-type": "application/json; charset=utf-8",
        "X-Hume-Api-Key": os.getenv("HUME_API_KEY"),
    }

    response = requests.post(url, data=payload, headers=headers)
    return response

# Function to process the recording and generate a response
def process_recording(recording_url):
    print("Starting: process_recording...")
    # Convert recording to text using speech-to-text API or library
    # Here, let's assume we have a function called `convert_speech_to_text` for this purpose
    recipient_message = convert_speech_to_text(recording_url)

    print("Generating response...", end="")
    # Generate a response using OpenAI
    print(recipient_message)
    generated_response = interaction(recipient_message)
    print("Done!")
    print("\t Generated response: ", generated_response)

    print("Saving response as audio...", end="")
    # Save the generated response as an audio url
    audio_url = save_generated_response_as_audio(generated_response)
    print("Done!")
    print("Sending response to recipient...", end="")
    return audio_url, generated_response


# Function to save the generated response as an audio file
def save_generated_response_as_audio(generated_response):
    conversational_style_id = "6434632c9f50eacb088edafd"
    marcus_speaker_id = "643463179f50eacb088edaec"

    url = "https://api.fliki.ai/v1/generate/text-to-speech"
    headers = {
        "Authorization": f"Bearer {os.getenv('FLIKI_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "content": generated_response,
        "voiceId": marcus_speaker_id,
        "voiceStyleId": conversational_style_id
    }
    
    response = requests.post(url, headers=headers, json=data)

    # Check the response status code
    if response.status_code == 200:
        # Process the response
        audio_data = response.content
        # Do something with the audio data
        response_dict = json.loads(audio_data)

        # Now you can access the dictionary elements
        success = response_dict["success"]
        audio_url = response_dict["data"]["audio"]
        duration = response_dict["data"]["duration"]
        
        return audio_url
    else:
        # Handle the error
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
    
    
def post_to_client(message, sender):
    url = "http://127.0.0.1:8201/post_to_client"
    data = {"message": message, "sender": sender}
    requests.post(url, data=data)


