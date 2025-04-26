from flask import Flask, Response
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """Generate TwiML response for incoming calls"""
    response = VoiceResponse()
    
    # Add a greeting message
    response.say("Hello! This is an automated call from your Fetch.ai agent.", voice="alice")
    
    # Add a pause
    response.pause(length=1)
    
    # Add more information
    response.say("This call was initiated by your automated agent.", voice="alice")
    
    # Add another pause
    response.pause(length=1)
    
    # End the call
    response.hangup()
    
    return Response(str(response), mimetype='text/xml')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 