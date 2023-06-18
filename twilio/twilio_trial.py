import time
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather, Start, Connect, Stream, Stop
from twilio.rest import Client
from dotenv import load_dotenv
import time
import os
import logging

from helper_funcitons import *

# Load environment variables from .env file
load_dotenv()

recordings = []
recording_chunks = False
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

# Twilio account credentials
account_sid = os.getenv("ACCOUNT_SID")
auth_token = os.getenv("AUTH_TOKEN")
client = Client(account_sid, auth_token)

app = Flask(__name__)

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# clear the outputs folder
for file in os.listdir(os.path.join(CURRENT_DIR, "outputs")):
    os.remove(os.path.join(CURRENT_DIR, "outputs", file))

@app.route("/start_call", methods=['GET'])
# @app.route("/outbound", methods=['GET'])
def outbound_call():
    try:
        logger.info("Outbound call initiated.")
        call = client.calls.create(
            url="https://fdcf-2607-f140-400-a034-a957-e34-ef52-36e6.ngrok-free.app/" + "conversation",  # Set the URL to the conversation endpoint
            from_='+18448925795',
            to='+15104672510'
        )
        return "Dialing..."
    except Exception as e:
        logger.error("Error during outbound call:", exc_info=True)
        return str(e)

@app.route("/conversation", methods=['POST'])
def conversation():
    global recordings
    print(recordings)
    with open('voice_detection.txt', 'w') as file:
        file.write('')  # Empty the file content
    response = VoiceResponse()
    if recordings:
        print("Dealing with the recording.")
        combined_audio = combine_audios(recordings, "outputs/output_{}.mp3".format(count_files_in_directory("./outputs")))
        recordings = []
        recipient_message, text = handle_recording_input(combined_audio)
        if len(text) > 0:
            response.pause()
            if "bye" in text.lower():
                response.hangup()
            else:
                if "/user" in text.lower():
                    user_info = None
                    while user_info is None:
                        response.pause()
                        user_info = input(text.split('/user')[1])
                    recipient_message = user_info
                start = response.start()
                start.stream(url='wss://c429-2607-f140-400-a034-a957-e34-ef52-36e6.ngrok-free.app/ws')
                response.play(recipient_message)    
                stop = response.stop()
                stop.stream()
    # start = response.start()
    # start.stream(url='wss://c429-2607-f140-400-a034-a957-e34-ef52-36e6.ngrok-free.app/audio_detection')
    # Streaming is complicated.
    response.record(max_length=5, timeout=2, play_beep=False, action="./handle_recording", trim='trim-silence')
    return str(response)


@app.route("/handle_recording", methods=['POST'])
def handle_recording():
    global recording_chunks
    global recordings
    # This will be triggered by Twilio once the audio recording is finished
    # Here you can handle the recorded audio and control the next step of the conversation
    voice_not_detected = False
    with open('voice_detection.txt', 'r') as file:
        voice_not_detected = file.read() == 'yes'
    response = VoiceResponse()
    if voice_not_detected:
        response.redirect("./conversation")
    else:
        # Continue chunking.
        url = request.values.get('RecordingUrl', None)
        recordings.append(url)
        print(url)
        print("Done with recording this one.")
        speech_detected = detect_speech_with_noise_reduction(url)
        if (speech_detected):
            response.record(max_length=5, timeout=2, action='/handle_recording', play_beep=False, trim='trim-silence')
        response.redirect("./conversation")
    
    return str(response)

def handle_recording_input(file_path):
    num_files = count_files_in_directory(CURRENT_DIR + "/outputs")

    # Ensure the file exists
    if os.path.exists(file_path):
        # Upload the file to Wasabi
        upload_file_to_wasabi(file_path, "blueberryai-input")
        url_to_play, text = process_recording("outputs/output_{}.mp3".format(num_files-1))
    else:
        print('File does not exist.')
        url_to_play, text = None, None

    return url_to_play, text


@app.route("/handle_ending", methods=['POST'])
def handle_ending():
    try:
        resp = VoiceResponse()
        resp.say("Thank you for your time! Have a wonderful day.")
        return str(resp)
    except Exception as e:
        logger.error("Error during ending:", exc_info=True)
# Below here is mostly for testing stuff out.


@app.route("/inbound", methods=['POST'])
def inbound_call():
    try:
        resp = VoiceResponse()
        gather = Gather(input='speech', action='/process_speech')
        gather.say('Hello, please tell us the reason for your call.')
        resp.append(gather)
        return str(resp)
    except Exception as e:
        logger.error("Error during inbound call:", exc_info=True)
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
