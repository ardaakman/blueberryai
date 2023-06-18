import gunicorn 

if __name__ == "__main__":
    gunicorn("twilio_trial:app", port=5002, host="127.0.0.1", reload=True)