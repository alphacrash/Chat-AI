from flask import Flask
from flask import request
from twilio.rest import Client

app = Flask(__name__)

ACCOUNT_ID = "AC2f25b1a607f56d0a7977967a3f140160"
TWILIO_TOKEN = "87fee13c99fd6a1488a47b6a9da6d56b"
TWILIO_NUMBER = "whatsapp:+14155238886"

client = Client(ACCOUNT_ID, TWILIO_TOKEN)

def send_msg(msg, recipient):
    client.messages.create(
        body=msg,
        from_=TWILIO_NUMBER,
        to=recipient
    )

def process_msg(msg):
    response = ""
    if msg == "hi":
        response = "Hello, welcome to the stock market bot!"
    else:
        response = "Type hi to get started"
    return response

@app.route('/', methods=["GET"])
def hello_world():
    return {
        "message": "Hello, World!"
    }

@app.route('/webhook', methods=["POST"])
def webhook():
    f = request.form
    msg = f["Body"]
    sender = f["From"]
    response = process_msg(msg)
    send_msg(response, sender)
    return "OK", 200
