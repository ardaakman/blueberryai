from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

# Twilio account credentials
account_sid = os.getenv("SID")
auth_token = os.getenv("TWILIO_AUTH")
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
            url=request.url_root + "process_speech",  # Set the URL to the conversation endpoint
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
        gather = Gather(input='speech', action='/process_speech', method='POST')
        gather.say('Hello, welcome to the conversation. Please tell us the reason for your call.')
        resp.append(gather)
        return str(resp)
    except Exception as e:
        logger.error("Error during conversation:", exc_info=True)
        return str(e)

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
            gather.play('https://s3.us-west-1.wasabisys.com/simulator/OfkDUtaSXL4wuKkbbup2BEeiy.mp3')
            resp.append(gather)

        return str(resp)
    except Exception as e:
        logger.error("Error during speech processing:", exc_info=True)
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)