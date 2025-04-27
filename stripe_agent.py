import os
import requests
from uagents import Agent, Model, Context
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_url = os.getenv('API_URL', f"{os.getenv('NGROK_URL')}/charge")

agent = Agent()

class StripeChargeRequest(Model):
    email: str

@agent.on_message(model=StripeChargeRequest)
async def handle_charge(ctx: Context, sender: str, req: StripeChargeRequest):
    try:
        response = requests.post(api_url, json={"email": req.email})
        result = response.json()
        if result.get("success"):
            ctx.logger.info(f"Charge successful: {result.get('payment_intent')}")
        else:
            ctx.logger.error(f"Charge failed: {result.get('error')}")
    except Exception as e:
        ctx.logger.error(f"Error calling backend: {e}")

if __name__ == "__main__":
    agent.run()