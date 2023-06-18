import time
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather, Start, Connect, Stream
from twilio.rest import Client
from dotenv import load_dotenv
import os
import logging

from helper_funcitons import *

# Load environment variables from .env file
load_dotenv()

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

# Twilio account credentials
account_sid = os.getenv("ACCOUNT_SID")
auth_token = os.getenv("AUTH_TOKEN")
client = Client(account_sid, auth_token)

app = Flask(__name__)

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/outbound", methods=['GET'])
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
    try:
        resp = VoiceResponse()
        resp.say("Hi, tell us the problem!")
        resp.record(maxLength="30", action="/handle_recording", playBeep=False, timeout="5", finishOnKey="#")
        return str(resp)
    except Exception as e:
        logger.error("Error during conversation:", exc_info=True)
        return str(e)

@app.route("/websocket", methods=['POST'])
def handlewebsocket():
    print("Handling websocket")
    print(request.values)
    return "OK"

@app.route("/handle_recording", methods=['POST'])
def handle_recording():
    print("Dealing with recordings")
    recording_url = request.values.get('RecordingUrl', None)
    response = requests.get(recording_url, stream=True)
    print("creating a response")

    num_files = count_files_in_directory(CURRENT_DIR + "/outputs")
    # Ensure the request is successful
    if response.status_code == 200:
        # Open the file in write-binary mode and write the response content to it
        with open('outputs/output_{}.mp3'.format(num_files), 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
    else:
        print('Failed to download the file.')

    upload_file_to_wasabi("outputs/output_{}.mp3".format(num_files), "calhacksaudio")
    resp= VoiceResponse()
    resp.say("Give me one moment please.")
    resp.redirect('/ending')
    #Try using the recording url from wasabi to create a response.

    return str(resp)

@app.route("/ending", methods=['POST'])
def ending():
    try:
        resp = VoiceResponse()
        #fetch wasabi stuff and do recording.
        url_to_play = process_recording("https://s3.us-west-1.wasabisys.com/calhacksaudio/output_0.mp3")
        print(url_to_play)
        resp.play(url_to_play)
        resp.say("Thank you for your time! Have a wonderful day.")
    
    except Exception as e:
        logger.error("Error during ending:", exc_info=True)
        return str(e)

        



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

@app.route("/process_speech", methods=['POST'])
def process_speech():
    try:
        speech_result = request.form.get('SpeechResult', '')
        resp = VoiceResponse()
        print("here")
        if 'sales' in speech_result.lower():
            resp.say('You mentioned sales. Redirecting your call to our sales department.', voice="Polly.Stephen-Neural", language="en-US")
            # Add the dial logic here if necessary
        elif 'support' in speech_result.lower():
            resp.say('You mentioned support. Redirecting your call to our support department.', voice="Polly.Stephen-Neural", language="en-US")
            # Add the dial logic here if necessary
        else:
            resp.say("I did not understand. Please say it again.")
            gather = Gather(input='speech', action='/process_speech')
            gather.play('https://storage.googleapis.com/fliki/media/api/642f37f4bac5767aff0b07bc/6467540cd30647acad0d8897.mp3')
            print("Done with response. Moving onto input.")
            resp.append(gather)
            resp.record(maxLength="30", action="/handle_recording")

        return str(resp)
    except Exception as e:
        logger.error("Error during speech processing:", exc_info=True)
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
