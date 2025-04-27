"""
This agent attempts to book a restaurant table by sending requests
"""

import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from dotenv import load_dotenv
from uagents import Agent, Context, Model
from pydantic import Field

load_dotenv()

class CallRequest(Model):
    phone_number: str = Field(default="+16476872539")  # Placeholder number
    task: str = Field(default="Complete your project")  # Placeholder task
    time_remaining: str = Field()

# Initialize agent
agent = Agent()

# Configuration
api_url = os.getenv('API_URL', f'{os.getenv('NGROK_URL')}/make-call')
start_time = datetime.now()
end_time = start_time + timedelta(hours=1)  # 1 hour timer

@agent.on_event("startup")
async def startup(ctx: Context):
    """Initialize the agent and start the timer"""
    ctx.logger.info("Call agent started")
    await make_call(ctx)

async def make_call(ctx: Context):
    """Make a call using the OpenAI endpoint"""
    while True:
        time_left = end_time - datetime.now()
        if time_left.total_seconds() <= 0:
            ctx.logger.info("Timer expired")
            break

        # Format time remaining
        hours = int(time_left.total_seconds() // 3600)
        minutes = int((time_left.total_seconds() % 3600) // 60)
        time_remaining = f"{hours} hours and {minutes} minutes"

        # Create call request
        request_data = {
            "phone_number": "+16476872539",
            "task": "Complete your project",
            "time_remaining": time_remaining
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=request_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        ctx.logger.info(f"Call initiated with SID: {result.get('call_sid')}")
                    else:
                        ctx.logger.error(f"Failed to make call: {response.status}")
        except Exception as e:
            ctx.logger.error(f"Error making call: {e}")

if __name__ == "__main__":
    agent.run()    
    