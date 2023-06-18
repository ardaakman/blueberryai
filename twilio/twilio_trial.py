import time
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather, Start, Connect, Stream, Stop
from twilio.rest import Client
from dotenv import load_dotenv
import os
import logging

from helper_funcitons import *

# Load environment variables from .env file
load_dotenv()

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

record_seconds = 7
number_of_times_so_far = 0
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
    #Functionality for initially listening to the user will be here.
    try:
        resp = VoiceResponse()
        resp.record(maxLength=record_seconds, action="/handle_recording", playBeep=False, timeout="3", finishOnKey="#")
        return str(resp)
    except Exception as e:
        logger.error("Error during conversation:", exc_info=True)
        return str(e)

@app.route("/handle_recording", methods=['POST'])
def handle_recording():
    global number_of_times_so_far
    resp= VoiceResponse()
    if (number_of_times_so_far == 7):
        resp.redirect("/handle_ending")
    print("Dealing with recording")
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

    upload_file_to_wasabi("outputs/output_{}.mp3".format(num_files), "blueberryai-input")
    resp= VoiceResponse()
    start = resp.start()
    start.stream(url='wss://c429-2607-f140-400-a034-a957-e34-ef52-36e6.ngrok-free.app/ws')
    print(num_files)
    url_to_play = process_recording("https://s3.us-west-1.wasabisys.com/blueberryai-input/output_{}.mp3".format(num_files))
    # start.stream()
    resp.play(url_to_play)
    stop= resp.stop()
    stop.stream()
    # Get the data from the FastAPI application
    response = requests.get('https://c429-2607-f140-400-a034-a957-e34-ef52-36e6.ngrok-free.app/get_data')
    data_received = response.json()
    print(f"Data received from WebSocket: {data_received}")
    number_of_times_so_far += 1
    resp.redirect('/conversation')
    #Try using the recording url from wasabi to create a response.

    return str(resp)

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


        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
