# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from configs import *

client = Client(account_sid, auth_token)

def call(to):
    to = "9495016532"
    call = client.calls.create(
        # url='https://handler.twilio.com/twiml/EH9c51bf5611bc2091f8d417b4ff44d104',
        url='https://410b-2607-f140-400-a011-20c1-f322-4b13-4bc9.ngrok-free.app/convo',
        to="+1" + to,
        from_="+18777192546"
    )
    print(call.sid)


call(1)