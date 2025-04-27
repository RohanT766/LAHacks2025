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
    phone_number: str
    task: str
    time_remaining: str

# Initialize agent
agent = Agent()

# Configuration
api_url = os.getenv('API_URL', 'https://e9f1-164-67-70-232.ngrok-free.app/send-message')
start_time = datetime.now()
end_time = start_time + timedelta(hours=1)  # 1 hour timer

@agent.on_event("startup")
async def startup(ctx: Context):
    """Initialize the agent and start the timer"""
    ctx.logger.info("Call agent started")
    # Schedule the first call immediately
    #await make_call(ctx)

@agent.on_message(model=CallRequest)
async def send_message(ctx: Context, sender: str, req: CallRequest):
    """Make a call using the OpenAI endpoint"""
    time_left = end_time - datetime.now()
    if time_left.total_seconds() <= 0:
        ctx.logger.info("Timer expired")
        return

    # Create call request
    request_data = {
        "phone_number": req.phone_number,
        "task": req.task,
        "time_remaining": req.time_remaining
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=request_data) as response:
                if response.status == 200:
                    result = await response.json()
                    ctx.logger.info(result.get('message'))
                else:
                    ctx.logger.error(f"Failed to make call: {response.status}")
    except Exception as e:
        ctx.logger.error(f"Error making call: {e}")

if __name__ == "__main__":
    agent.run()    
    