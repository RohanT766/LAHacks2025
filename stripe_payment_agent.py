import os
import requests
from uagents import Agent, Model, Context
from dotenv import load_dotenv

load_dotenv()

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_API_URL = "https://api.stripe.com/v1/payment_intents"

agent = Agent()

class StripePaymentRequest(Model):
    payment_method_id: str   # Required, the payment method to charge
    customer_id: str = None  # Optional, if you want to charge a customer
    description: str = "Charge for $5"

@agent.on_message(model=StripePaymentRequest)
async def handle_payment(ctx: Context, sender: str, req: StripePaymentRequest):
    headers = {
        "Authorization": f"Bearer {STRIPE_SECRET_KEY}"
    }
    data = {
        "amount": 500,  # $5 in cents
        "currency": "usd",
        "payment_method": req.payment_method_id,
        "confirmation_method": "automatic",
        "confirm": "true",
        "description": req.description,
    }
    if req.customer_id:
        data["customer"] = req.customer_id

    response = requests.post(STRIPE_API_URL, headers=headers, data=data)
    if response.status_code == 200:
        ctx.logger.info(f"Payment successful: {response.json()}")
    else:
        ctx.logger.error(f"Payment failed: {response.text}")

if __name__ == "__main__":
    agent.run() 