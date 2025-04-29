import os
import io
import base64
import tempfile
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient, ASCENDING
from bson import ObjectId
import bcrypt
import stripe
import tweepy  # type: ignore[import]
from PIL import Image
import numpy as np
import cv2
from google.generativeai import GenerativeModel, configure
import traceback
from image_validator import validate_task_image

# Load environment
load_dotenv()
stripe.api_key       = os.getenv("STRIPE_SECRET_KEY")
TWITTER_API_KEY      = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET   = os.getenv("TWITTER_API_SECRET")
TWITTER_CALLBACK_URL = os.getenv("TWITTER_CALLBACK_URL")
SESSION_SECRET       = os.getenv("SESSION_SECRET")
GEMINI_API_KEY       = os.getenv("GEMINI_API_KEY")

# Configure Gemini
configure(api_key=GEMINI_API_KEY)
gemini = GenerativeModel("gemini-1.5-flash")

# MongoDB
MONGO_URL    = os.getenv("MONGO_URL")
MONGO_DBNAME = os.getenv("MONGO_DB", "lahacks25")
client: MongoClient[Any] = MongoClient(MONGO_URL, tls=True, tlsCAFile=certifi.where())
db: Any = client[MONGO_DBNAME]

# Ensure indexes
db.users.create_index([("email", ASCENDING)], unique=True)
db.users.create_index([("tasks.due_date", ASCENDING)])

# FastAPI setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware, secret_key=SESSION_SECRET,
    session_cookie="session", max_age=14*24*3600, same_site="lax"
)

# Serve UI
@app.get("/", include_in_schema=False)
def serve_ui():
    return FileResponse("static/index.html")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Models
class PhotoVerification(BaseModel):
    user_id: str
    task_id: str
    photo_data: str  # Data URI (base64)

class RegisterUser(BaseModel):
    email: str
    password: str
    nickname: str
    phone: str

class LoginUser(BaseModel):
    email: str
    password: str

# --- Task Models ---
class TaskAdd(BaseModel):
    user_id: str = Field(..., description="MongoDB ObjectId string for the user")
    description: str
    frequency: str
    charity_id: str = Field(..., description="MongoDB ObjectId string for the charity")
    donation_amount: int  # in cents
    due_date: datetime

class TaskReport(BaseModel):
    user_id: str = Field(..., description="MongoDB ObjectId string for the user")
    task_id: str = Field(..., description="MongoDB ObjectId string for the task")
    did_task: bool

class CharityAdd(BaseModel):
    name: str
    stripe_account_id: str

# Add this model for party update
class PartyUpdate(BaseModel):
    user_id: str
    party: str

# --- Auth Endpoints ---
@app.post("/register")
def register(user: RegisterUser):
    # check for existing email
    if db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="The user already exists")
    # create stripe customer
    try:
        customer = stripe.Customer.create(email=user.email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {e}")
    # hash password
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    # insert user with empty tasks list
    doc = {
        "email": user.email,
        "password": hashed_pw,
        "nickname": user.nickname,
        "stripe_customer_id": customer.id,
        "phone": user.phone,
        "tasks": []
    }
    res = db.users.insert_one(doc)
    return {"message": "User created", "user_id": str(res.inserted_id), "stripe_customer_id": customer.id}

@app.post("/login")
def login(credentials: LoginUser):
    user = db.users.find_one({"email": credentials.email})
    if not user or not bcrypt.checkpw(credentials.password.encode('utf-8'), user['password']):
        raise HTTPException(status_code=401, detail="Wrong username or password")
    return {"user_id": str(user['_id']), "nickname": user.get('nickname'), "email": user['email']}

# --- Charity Endpoints ---
@app.get("/charities")
def get_charities():
    try:
        charities = list(db.charities.find({}, {"_id": 1, "name": 1}))
        # Convert ObjectId to string for JSON serialization
        for charity in charities:
            charity["_id"] = str(charity["_id"])
        return charities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching charities: {str(e)}")

@app.post("/charity")
def add_charity(charity: CharityAdd):
    res = db.charities.insert_one({
        "name": charity.name,
        "stripe_account_id": charity.stripe_account_id
    })
    return {"message": "Charity added", "charity_id": str(res.inserted_id)}

# --- Task Endpoints ---
@app.post("/task")
def add_task(t: TaskAdd):
    try:
        # validate user
        if not ObjectId.is_valid(t.user_id):
            raise HTTPException(status_code=400, detail="Invalid user_id format")
        
        user_obj = db.users.find_one({"_id": ObjectId(t.user_id)})
        if not user_obj:
            raise HTTPException(status_code=404, detail=f"User {t.user_id} not found")
        
        # validate charity
        if not ObjectId.is_valid(t.charity_id):
            raise HTTPException(status_code=400, detail="Invalid charity_id format")
            
        charity_obj = db.charities.find_one({"_id": ObjectId(t.charity_id)})
        if not charity_obj:
            raise HTTPException(status_code=404, detail=f"Charity {t.charity_id} not found")
        
        # create task entry
        task_id = ObjectId()
        task_doc = {
            "_id": task_id,
            "description": t.description,
            "frequency": t.frequency,
            "charity_id": ObjectId(t.charity_id),
            "donation_amount": t.donation_amount,
            "due_date": t.due_date,
            "did_task": False
        }
        
        result = db.users.update_one(
            {"_id": ObjectId(t.user_id)}, 
            {"$push": {"tasks": task_doc}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to add task to user")
            
        return {"message": "Task added", "task_id": str(task_id)}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/report-task")
def report_task(report: TaskReport):
    # validate identifiers
    if not ObjectId.is_valid(report.user_id) or not ObjectId.is_valid(report.task_id):
        raise HTTPException(status_code=400, detail="Invalid ID(s)")
    # update did_task flag inside tasks array
    upd = db.users.update_one(
        {"_id": ObjectId(report.user_id)},
        {"$set": {"tasks.$[elem].did_task": report.did_task}},
        array_filters=[{"elem._id": ObjectId(report.task_id)}]
    )
    if upd.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": f"Recorded did_task={report.did_task} for task {report.task_id}"}

@app.get("/login/twitter")
async def twitter_login(request: Request):
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        callback=TWITTER_CALLBACK_URL
    )
    try:
        redirect_url = auth.get_authorization_url()
    except Exception as e:
        raise HTTPException(500, f"Twitter OAuth init failed: {e}")
    request.session["request_token_secret"] = auth.request_token["oauth_token_secret"]
    return RedirectResponse(redirect_url)

@app.get("/callback/twitter")
async def twitter_callback(request: Request):
    oauth_token    = request.query_params.get("oauth_token")
    oauth_verifier = request.query_params.get("oauth_verifier")
    if not oauth_token or not oauth_verifier:
        raise HTTPException(400, "Missing oauth_token or oauth_verifier")

    # Re-create handler with the saved request token secret
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        callback=TWITTER_CALLBACK_URL
    )
    auth.request_token = {
        "oauth_token": oauth_token,
        "oauth_token_secret": request.session.pop("request_token_secret", None)
    }

    # Exchange for access tokens
    access_token, access_token_secret = auth.get_access_token(oauth_verifier)

    # Create an API client and fetch the user's profile
    api = tweepy.API(auth)
    profile = api.verify_credentials()
    twitter_id  = str(profile.id)
    screen_name = profile.screen_name

    # Create Twitter object in the correct format
    twitter_obj = {
        "id": twitter_id,
        "access_token": access_token,
        "access_token_secret": access_token_secret,
        "screen_name": screen_name
    }

    # Upsert into your users collection
    result = db.users.update_one(
        {"twitter.id": twitter_id},
        {"$set": {
            "twitter": twitter_obj
        }},
        upsert=True
    )

    existing = db.users.find_one({"twitter.id": twitter_id})
    if existing is None:
        raise HTTPException(500, "Failed to look up existing Twitter user")

    assert existing is not None

    user_obj_id = str(existing["_id"])

    # Create the redirect URL
    redirect_url = f"youwontforget://twitter-callback?user_id={user_obj_id}&screen_name={screen_name}"

    # Return HTML that will handle the redirect
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Twitter Login Success</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                background-color: #f5f5f5;
            }}
            .container {{
                text-align: center;
                padding: 20px;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #1DA1F2;
                margin-bottom: 20px;
            }}
            p {{
                color: #333;
                margin-bottom: 20px;
            }}
            button {{
                background-color: #1DA1F2;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }}
            button:hover {{
                background-color: #1991da;
            }}
        </style>
        <script>
            // Function to redirect to the app
            function redirectToApp() {{
                // Try to open the app directly
                window.location.href = "{redirect_url}";
                
                // If that fails, show the button after a short delay
                setTimeout(function() {{
                    document.getElementById('redirectButton').style.display = 'block';
                }}, 1000);
            }}

            // Try to redirect immediately
            redirectToApp();
        </script>
    </head>
    <body>
        <div class="container">
            <h1>Login Successful!</h1>
            <p>You've successfully logged in with Twitter.</p>
            <button id="redirectButton" onclick="redirectToApp()" style="display: none;">Return to App</button>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# Donation check replaces routines logic
async def check_and_donate():
    now = datetime.utcnow()
    for user in db.users.find():
        for task in user.get('tasks', []):
            # skip if already done or no donation needed
            if task.get('did_task'):
                continue
            
            # TODO: implement frequency logic based on task['frequency'] and task['due_date']

            c = db.charities.find_one({"_id": task['charity_id']})
            if not c:
                continue
            try:
                print(f"Donating ${task['donation_amount']/100:.2f} from {user['email']} to {c['name']} for '{task['description']}'")
            except Exception as e:
                print(f"Error donating for task {task['_id']}: {e}")
            # reset did_task
            db.users.update_one(
                {"_id": user['_id']},
                {"$set": {"tasks.$[elem].did_task": False}},
                array_filters=[{"elem._id": task['_id']}]   
            )

@app.post("/run-donations")
def run_donations(background_tasks: BackgroundTasks):
    background_tasks.add_task(check_and_donate)
    return {"message": "Donation check started in background"}

@app.get("/tasks/{user_id}")
def get_user_tasks(user_id: str):
    try:
        # validate user
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user_id format")
        
        user_obj = db.users.find_one({"_id": ObjectId(user_id)})
        if not user_obj:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        # get tasks
        tasks = user_obj.get('tasks', [])
        
        # convert ObjectIds to strings
        for task in tasks:
            task['_id'] = str(task['_id'])
            task['charity_id'] = str(task['charity_id'])
        
        return tasks
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/verify-task-photo")
async def verify_task_photo(v: PhotoVerification):
    try:
        print("\n=== Starting Task Photo Verification ===")
        print(f"Received request - user_id: {v.user_id}, task_id: {v.task_id}")
        
        # Validate user and task
        if not ObjectId.is_valid(v.user_id) or not ObjectId.is_valid(v.task_id):
            print(f"Invalid IDs - user_id: {v.user_id}, task_id: {v.task_id}")
            raise HTTPException(status_code=400, detail="Invalid user_id or task_id")
        
        user = db.users.find_one({"_id": ObjectId(v.user_id)})
        if not user:
            print(f"User not found: {v.user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        # Find the task in the user's tasks array
        task = None
        for t in user.get('tasks', []):
            if str(t['_id']) == v.task_id:
                task = t
                break
        
        if not task:
            print(f"Task not found: {v.task_id}")
            raise HTTPException(status_code=404, detail="Task not found")

        print(f"Found task: {task.get('description')}")
        print("Validating image with Gemini...")

        try:
            # Validate the image using Gemini
            is_valid = validate_task_image(task.get('description', 'the assigned task'), v.photo_data)
            print(f"Image validation result: {'valid' if is_valid else 'invalid'}")

            if is_valid:
                try:
                    print("Updating task status in database...")
                    print(f"Updating task {v.task_id} for user {v.user_id}")
                    
                    # First verify the task exists
                    task_exists = db.users.find_one({
                        "_id": ObjectId(v.user_id),
                        "tasks._id": ObjectId(v.task_id)
                    })
                    
                    if not task_exists:
                        print(f"Task {v.task_id} not found in user's tasks")
                        raise HTTPException(404, "Task not found in user's tasks")
                    
                    # Update the task status
                    result = db.users.update_one(
                        {"_id": ObjectId(v.user_id)},
                        {"$set": {"tasks.$[elem].did_task": True}},
                        array_filters=[{"elem._id": ObjectId(v.task_id)}]
                    )
                    
                    if result.matched_count == 0:
                        print(f"No matching document found for user {v.user_id}")
                        raise HTTPException(404, "User document not found")
                        
                    if result.modified_count == 0:
                        print(f"Task {v.task_id} was not modified")
                        raise HTTPException(500, "Failed to update task status")
                    
                    print(f"Successfully updated task {v.task_id} for user {v.user_id}")
                    return {"success": True, "message": "Task verified and completed"}
                    
                except HTTPException as he:
                    print(f"HTTP Exception during task update: {he.detail}")
                    raise he
                except Exception as e:
                    print(f"Error updating task status: {str(e)}")
                    print(f"Traceback: {traceback.format_exc()}")
                    raise HTTPException(500, f"Database error: {str(e)}")
            else:
                print("Image verification failed")
                return {"success": False, "message": "Photo verification failed - image does not clearly show task completion"}

        except HTTPException as he:
            print(f"HTTP Exception in image validation: {he.detail}")
            print(f"Traceback: {traceback.format_exc()}")
            raise he
        except Exception as e:
            print(f"Unexpected error in image validation: {str(e)}")
            print(f"Error type: {type(e)}")
            print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details available'}")
            print(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

    except HTTPException as he:
        print(f"HTTP Exception in verify-task-photo: {he.detail}")
        print(f"Traceback: {traceback.format_exc()}")
        raise he
    except Exception as e:
        print(f"Unexpected error in verify-task-photo: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details available'}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        print("=== Task Photo Verification Complete ===\n")

@app.post("/update-party")
def update_party(update: PartyUpdate):
    try:
        # Validate user ID
        if not ObjectId.is_valid(update.user_id):
            raise HTTPException(status_code=400, detail="Invalid user_id format")
        
        # Update user's party in database
        result = db.users.update_one(
            {"_id": ObjectId(update.user_id)},
            {"$set": {"political_party": update.party}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {"message": "Party updated successfully"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/user-party/{user_id}")
def get_user_party(user_id: str):
    try:
        # Validate user ID
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user_id format")
        
        # Get user's party from database
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {"party": user.get("political_party", "Unknown")}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)