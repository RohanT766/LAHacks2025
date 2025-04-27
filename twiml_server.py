from flask import Flask, Response
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    response = VoiceResponse()
    response.say("Hello! This is a test call from your Twilio application.", voice="alice")
    return Response(str(response), mimetype='text/xml')

@app.route("/answer", methods=['GET', 'POST'])
def answer():
    response = VoiceResponse()
    response.say("Hello! This is a test call from your Twilio application.", voice="alice")
    return Response(str(response), mimetype='text/xml')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000) 