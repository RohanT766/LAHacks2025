import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client
from fetchai.agents import Agent

# Load environment variables
load_dotenv()

class CallAgent(Agent):
    def __init__(self):
        super().__init__()
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.target_number = os.getenv('TARGET_PHONE_NUMBER')
        self.client = Client(self.account_sid, self.auth_token)
        self.call_interval = 300  # 5 minutes in seconds
        self.twiml_url = "http://localhost:5000/voice"  # Local TwiML server URL

    async def setup(self):
        """Initialize the agent"""
        print(f"Call Agent initialized. Will call {self.target_number} every 5 minutes.")

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
        """Main agent loop"""
        while True:
            await self.make_call()
            await asyncio.sleep(self.call_interval)

async def main():
    # Create and run the agent
    agent = CallAgent()
    await agent.setup()
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main()) 