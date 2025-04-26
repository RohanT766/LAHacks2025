from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get Twilio credentials from environment variables
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

# Initialize Twilio client
client = Client(account_sid, auth_token)

def call_user(user_phone_number):
    try:
        call = client.calls.create(
            url='https://your-server.com/voice-instructions',  # XML or dynamic voice URL
            to=user_phone_number,
            from_=twilio_phone_number
        )
        print(f"Call started: {call.sid}")
        return call
    except Exception as e:
        print(f"Error making call: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    # Replace with actual phone number
    test_number = "+16476872539"
    call_user(test_number)
