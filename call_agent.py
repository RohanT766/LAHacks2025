import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

class CallAgent:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.target_number = os.getenv('TARGET_PHONE_NUMBER')
        self.client = Client(self.account_sid, self.auth_token)
        self.call_interval = 300  # 5 minutes in seconds
        self.twiml_url = "https://d6dd-164-67-70-232.ngrok-free.app"  # Local TwiML server URL

    async def make_call(self):
        """Make a call using Twilio"""
        try:
            call = self.client.calls.create(
                url=self.twiml_url,  # Using our local TwiML server
                to=self.target_number,
                from_=self.twilio_number
            )
            print(f"[{datetime.now()}] Call initiated: {call.sid}")
        except Exception as e:
            print(f"[{datetime.now()}] Error making call: {e}")

    async def run(self):
        """Run the agent"""
        print(f"Call Agent initialized. Will call {self.target_number} every 5 minutes.")
        print("First call will be made in 10 seconds...")
        await asyncio.sleep(10)  # Wait 10 seconds before first call
        
        while True:
            await self.make_call()
            await asyncio.sleep(self.call_interval)

if __name__ == "__main__":
    agent = CallAgent()
    asyncio.run(agent.run()) 