from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import time
import openai
# Set up Twilio client
account_sid = os.getenv("SID")
auth_token = os.getenv("TWILIO_AUTH")
twilio_phone_number = "+18448925795"
recipient_phone_number = "+15104672510"
client = Client(account_sid, auth_token)
# Set up OpenAI
openai.api_key = "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"
# Function to generate response using OpenAI
def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
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
    response.record(max_length=30, action="/process_recording")
    return str(response)
# Function to process the recording and generate a response
def process_recording(recording_url):
    # Convert recording to text using speech-to-text API or library
    # Here, let’s assume we have a function called `convert_speech_to_text` for this purpose
    recipient_message = convert_speech_to_text(recording_url)
    # Generate a response using OpenAI
    prompt = "Recipient said: + recipient_message"
    generated_response = generate_response(prompt)
    # Respond to the recipient with the generated answer
    response = VoiceResponse()
    response.say(generated_response)
    response.record(max_length=30, action=‘/process_recording’)
    return str(response)
# Create a Twilio call
call = client.calls.create(
    twiml=handle_incoming_call(),
    to=recipient_phone_number,
    from_=twilio_phone_number
)
# Twilio webhook to process the recording and generate a response
@app.route(‘/process_recording’, methods=[‘POST’])
def process_recording_webhook():
    recording_url = request.form[‘RecordingUrl’]
    response = process_recording(recording_url)
    return response
# Start the Flask server to listen for incoming requests
if __name__ == ‘__main__‘:
    app.run()