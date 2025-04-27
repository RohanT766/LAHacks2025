"""
This agent handles restaurant table booking requests using a MongoDB Atlas database.
"""
import os
from datetime import datetime, timedelta, timezone
from uagents import Agent, Model, Context, Protocol
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from dateutil import parser  # Added for date parsing

load_dotenv()

# Initialize agent
agent = Agent()

# For this example, you will need to set up an account and database on MongoDB Atlas:
# https://www.mongodb.com/atlas/database. Once you have done so, enter your details
# into the agent's .env file. And set the password as an agent secret.

# MongoDB Configuration
MONGO_USER = os.environ.get("MONGO_USER")
MONGO_HOST_URL = os.environ.get("MONGO_HOST_URL")
MONGO_PASSWORD_2 = os.environ.get("MONGO_PASSWORD_2")

uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD_2}@{MONGO_HOST_URL}retryWrites=true&w=majority"
print(uri)
client = MongoClient(uri, server_api=ServerApi('1'))

db = client.lahacks25
users = db["users"]

# Time thresholds for notifications (in hours)
TEXT_THRESHOLDS = [72, 48, 24, 12, 6]  # 3 days, 2 days, 1 day, 12 hours, 6 hours
CALL_THRESHOLDS = [2, 1, 0.83, 0.67, 0.5, 0.33, 0.17]  # 2 hours, 1 hour, 50 min, 40 min, 30 min, 20 min, 10 min
CHARGE_THRESHOLDS = [0, 24, 48, 72]  # Due date, 1 day late, 2 days late, 3 days late
TWEET_THRESHOLDS = [12, 36, 60, 84]  # 12 hours late, 1.5 days late, 2.5 days late, 3.5 days late

class Task(Model):
    name: str
    due_date: datetime
    completed: bool = False

class User(Model):
    phone_number: str
    tasks: list[Task]

class CallRequest(Model):
    phone_number: str
    task: str
    time_remaining: str


class TweetRequest(Model):
    access_token: str
    access_token_secret: str
    text: str

class StripeChargeRequest(Model):
    email: str

def check_time_threshold(task_due: datetime, threshold_hours: float) -> bool:
    """Check if current time is within 10 minutes after a threshold time"""
    now = datetime.now(timezone.utc)
    threshold_time = task_due - timedelta(hours=threshold_hours)
    time_diff = now - threshold_time
    return 0 <= time_diff.total_seconds() <= 60  # 10 minutes in seconds

def check_overdue_threshold(task_due: datetime, hours_overdue: float) -> bool:
    """Check if current time is within 10 minutes after an overdue threshold time"""
    now = datetime.now(timezone.utc)
    threshold_time = task_due + timedelta(hours=hours_overdue)
    time_diff = now - threshold_time
    return 0 <= time_diff.total_seconds() <= 60  # 10 minutes in seconds

async def send_text(ctx: Context, phone_number: str, task_name: str, time_left: str):
    """Placeholder for sending text messages"""
    print(f"Sending text to {phone_number}: 'Reminder: {task_name} is due in {time_left}'")
    await ctx.send('agent1qt8n3t425wlld4rjm5xtcf6ahqdewzq3g64lnze85l7l0xlkdz6rwpa9krq', CallRequest(phone_number=phone_number,task=task_name,time_remaining=time_left))

async def make_call(ctx: Context, phone_number: str, task_name: str, time_left: str):
    """Placeholder for making calls"""
    print(f"Calling {phone_number} about task '{task_name}' due in {time_left}")
    await ctx.send('agent1qgap4rk8dnvhez4fcaxc4za2337scadkfc7frd3v2s2tc44aw2d8cejydw9', CallRequest(phone_number=phone_number,task=task_name,time_remaining=time_left))

async def charge_user(ctx: Context, email: str):
    """Placeholder for charging users"""
    print(f"Charging {phone_number} for task '{task_name}' - {days_late:.1f} days late")
    await ctx.send('agent1q0ytn0q5lc6zm72288zewe8untpgutdjnjams00wwatdqnq6w9xgy69lstg', StripeChargeRequest(email=email))

async def force_tweet(ctx: Context, access_token: str, access_token_secret: str, task_name: str):
    """Placeholder for forcing tweets"""
    print(f"Forcing user to tweet about task {task_name}")
    await ctx.send('agent1qfhm6zhmms9eu7q7qjazvyva4jetc7n8hp8zw9ft5lef99fcfmxl6nj7kt4', TweetRequest(access_token=access_token, access_token_secret=access_token_secret, text=task_name))

@agent.on_interval(period=60.0)  # Check every minute
async def check_tasks(ctx: Context):
    """Check all tasks and send notifications if needed"""
    now = datetime.now(timezone.utc)
    
    # Get all users
    for user in users.find():
        #print(user)
        if user.get('tasks'):
            for task in user.get('tasks'):
                task_due = task['due_date']
                if isinstance(task_due, str):
                    task_due = parser.isoparse(task_due)
                if task_due.tzinfo is None:
                    task_due = task_due.replace(tzinfo=timezone.utc)
                #print(task['description'])
                time_left = task_due - now
                
                # Check text thresholds
                for threshold in TEXT_THRESHOLDS:
                    if check_time_threshold(task_due, threshold):
                        time_str = f"{threshold} hours" if threshold < 24 else f"{threshold//24} days"
                        await send_text(ctx, user['phone'], task['description'], time_str)
                        break
                        
                # Check call thresholds
                for threshold in CALL_THRESHOLDS:
                    if check_time_threshold(task_due, threshold):
                        time_str = f"{int(threshold*60)} minutes" if threshold < 1 else f"{int(threshold)} hours"
                        await make_call(ctx, user['phone'], task['description'], time_str)
                        break

                # Check overdue thresholds (after due date)
                if time_left.total_seconds() < 0:
                    # Calculate how many 12-hour periods have passed
                    hours_overdue = abs(time_left.total_seconds() / 3600)
                    periods_passed = int(hours_overdue / 12)
                    
                    # Check if we're at a 12-hour mark
                    if check_overdue_threshold(task_due, periods_passed * 12):
                        # Charge every 24 hours (every 2 periods)
                        if periods_passed % 2 == 0:
                            days_late = (periods_passed * 12) / 24
                            await charge_user(ctx, user['email'])
                        
                        # Force tweet every 12 hours
                        #hours_late = periods_passed * 12

                        if not user or 'twitter' not in user:
                            raise ValueError(f"No twitter object for user")
                        twitter = user['twitter']
                        access_token = twitter.get('access_token')
                        access_token_secret = twitter.get('access_token_secret')
                        if not access_token or not access_token_secret:
                            raise ValueError(f"No OAuth tokens found for user")

                        await force_tweet(ctx, access_token, access_token_secret, task['description'])

if __name__ == "__main__":
    agent.run()
    