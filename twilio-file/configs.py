import os

account_sid = "AC67673481da0305e4333f22ad00c296f0"
auth_token = "b9f76b0767b5c19ab7039dc84f9b5e66"
openai = "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"

# save to os.environ
os.environ["ACCOUNT_SID"] = account_sid
os.environ["AUTH_TOKEN"] = auth_token
os.environ["OPENAI_API_KEY"] = openai