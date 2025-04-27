import os
import bcrypt
import stripe
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient, ASCENDING
from bson import ObjectId
import tweepy # type: ignore[import]
from base64 import b64decode
import io
from PIL import Image
import numpy as np
import cv2

# Load environment and initialize Stripe
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

TWITTER_API_KEY       = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET    = os.getenv("TWITTER_API_SECRET")
TWITTER_CALLBACK_URL  = os.getenv("TWITTER_CALLBACK_URL") 
SESSION_SECRET = os.getenv("SESSION_SECRET")

# Database setup
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DBNAME = os.getenv("MONGO_DB", "lahacks25")
client: MongoClient = MongoClient(
    MONGO_URL,
    tls=True,
    tlsCAFile=certifi.where()
)
db = client[MONGO_DBNAME]

# Ensure indexes
# Unique users by email
db.users.create_index([("email", ASCENDING)], unique=True)
# Index tasks by due_date for efficient querying
db.users.create_index([("tasks.due_date", ASCENDING)])

# FastAPI app
app = FastAPI()

# 1) CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2) Sessions middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,        # ← required
    session_cookie="session",         # ← optional
    max_age=14 * 24 * 3600,           # ← optional
    same_site="lax",                  # ← optional
)

# Serve static UI
@app.get("/", include_in_schema=False)
async def serve_ui():
    return FileResponse("static/index.html")
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Auth Models ---
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

# Add this model for photo verification
class PhotoVerification(BaseModel):
    user_id: str
    task_id: str
    photo_data: str  # base64 encoded image

@app.post("/verify-task-photo")
async def verify_task_photo(verification: PhotoVerification):
    try:
        # Validate user and task
        if not ObjectId.is_valid(verification.user_id) or not ObjectId.is_valid(verification.task_id):
            raise HTTPException(status_code=400, detail="Invalid user_id or task_id")
        
        user = db.users.find_one({"_id": ObjectId(verification.user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Find the task in the user's tasks array
        task = None
        for t in user.get('tasks', []):
            if str(t['_id']) == verification.task_id:
                task = t
                break
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Decode base64 image
        try:
            image_data = b64decode(verification.photo_data.split(',')[1])
            image = Image.open(io.BytesIO(image_data))
            # Convert to numpy array for OpenCV
            image_np = np.array(image)
            # Convert RGB to BGR (OpenCV format)
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

        # TODO: Add your image verification logic here
        # For now, we'll just return True for testing
        is_valid = True

        if is_valid:
            # Remove the task from the user's tasks array
            result = db.users.update_one(
                {"_id": ObjectId(verification.user_id)},
                {"$pull": {"tasks": {"_id": ObjectId(verification.task_id)}}}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to remove task")
            
            return {"success": True, "message": "Task verified and removed"}
        else:
            return {"success": False, "message": "Photo verification failed"}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)