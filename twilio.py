from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

# Twilio account credentials
account_sid = 
auth_token = 
client = Client(account_sid, auth_token)

app = Flask(__name__)

@app.route("/outbound", methods=['GET'])
def outbound_call():
    call = client.calls.create(
        url='http://YOUR_SERVER_URL/inbound',
        to='to_phone_number',
        from_='from_phone_number'
    )
    return "Dialing..."

@app.route("/inbound", methods=['POST'])
def inbound_call():
    resp = VoiceResponse()
    gather = Gather(input='speech', action='/process_speech')
    gather.say('Hello, please tell us the reason for your call.')
    resp.append(gather)
    return str(resp)

@app.route("/process_speech", methods=['POST'])
def process_speech():
    speech_result = request.values.get('SpeechResult', '')
    resp = VoiceResponse()
    
    if 'sales' in speech_result.lower():
        resp.say('You mentioned sales. Redirecting your call to our sales department.')
        # Add the dial logic here if necessary
    elif 'support' in speech_result.lower():
        resp.say('You mentioned support. Redirecting your call to our support department.')
        # Add the dial logic here if necessary
    else:
        resp.say('Sorry, I did not understand that. Goodbye.')
    
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
