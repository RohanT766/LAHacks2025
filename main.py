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

# --- Charity Endpoint ---
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
    # validate user
    if not ObjectId.is_valid(t.user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id")
    user_obj = db.users.find_one({"_id": ObjectId(t.user_id)})
    if not user_obj:
        raise HTTPException(status_code=404, detail=f"User {t.user_id} not found")
    # validate charity
    if not ObjectId.is_valid(t.charity_id) or not db.charities.find_one({"_id": ObjectId(t.charity_id)}):
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
    db.users.update_one({"_id": ObjectId(t.user_id)}, {"$push": {"tasks": task_doc}})
    return {"message": "Task added", "task_id": str(task_id)}

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

    # Create an API client and fetch the user’s profile
    api = tweepy.API(auth)
    profile = api.verify_credentials()   # ← here’s the change
    twitter_id  = str(profile.id)
    screen_name = profile.screen_name

    # Upsert into your users collection as before…
    result = db.users.update_one(
        {"twitter.id": twitter_id},
        {"$set": {
            "twitter.id": twitter_id,
            "twitter.screen_name": screen_name,
            "twitter.access_token": access_token,
            "twitter.access_token_secret": access_token_secret,
        }},
        upsert=True
    )

    existing = db.users.find_one({"twitter.id": twitter_id})
    if existing is None:
        raise HTTPException(500, "Failed to look up existing Twitter user")

    assert existing is not None

    user_obj_id = existing["_id"]

    return HTMLResponse(f"""
      <html>
        <body>
          ✅ Logged in as @{screen_name}<br/>
          Your internal user_id is <code>{user_obj_id}</code>
        </body>
      </html>
    """)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)