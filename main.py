import os
import bcrypt
import stripe
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

MONGO_URL    = os.getenv("MONGO_URL")
MONGO_DBNAME = os.getenv("MONGO_DB", "lahacks25")
client: MongoClient = MongoClient(
    MONGO_URL,
    tls=True,
    tlsCAFile=certifi.where()
)
db = client[MONGO_DBNAME]

# ensure our indexes
db.users.create_index([("email", ASCENDING)], unique=True)
db.routines.create_index([("user_id", ASCENDING)])
db.routines.create_index([("charity_id", ASCENDING)])

app = FastAPI()

# Serve the SPA root
@app.get("/", include_in_schema=False)
async def serve_ui():
    return FileResponse("static/index.html")

# Mount static assets
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Auth Models ---
class RegisterUser(BaseModel):
    email: str
    password: str
    nickname: str

class LoginUser(BaseModel):
    email: str
    password: str

class VerifyEmail(BaseModel):
    email: str



# --- Auth Endpoints ---

@app.post("/register")
def register(user: RegisterUser):
    # ensure unique email
    if db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="The user already exists")

    # 1) create Stripe customer
    try:
        customer = stripe.Customer.create(email=user.email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {e}")

    # 2) hash password
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    # 3) insert new user, include stripe_customer_id
    doc = {
        "email": user.email,
        "password": hashed_pw,
        "nickname": user.nickname,
        "stripe_customer_id": customer.id,
        "email_verified": False
    }
    res = db.users.insert_one(doc)

    return {
        "message": "User created",
        "user_id": str(res.inserted_id),
        "stripe_customer_id": customer.id
    }


@app.post("/login")
def login(credentials: LoginUser):
    # find user by email
    user = db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(status_code=401, detail="Wrong username or password")

    # verify password
    if not bcrypt.checkpw(credentials.password.encode('utf-8'), user['password']):
        raise HTTPException(status_code=401, detail="Wrong username or password")

    # successful
    return {
        "user_id": str(user["_id"]),
        "nickname": user.get("nickname"),
        "email": user["email"]
    }

# We can implement later 
# @app.post("/verify-email")
# def verify_email(payload: VerifyEmail):
#     result = db.users.update_one(
#         {"email": payload.email, "email_verified": False},
#         {"$set": {"email_verified": True}}
#     )

#     # result.modified_count > 0 indicates we flipped from false → true
#     return {"verified": result.modified_count > 0}




class UserOnboard(BaseModel):
    email: str
    phone_number: int

class CharityAdd(BaseModel):
    name: str
    stripe_account_id: str

class RoutineAdd(BaseModel):
    user_id: str = Field(..., description="MongoDB ObjectId string for the user")
    description: str
    frequency: str
    charity_id: str = Field(..., description="MongoDB ObjectId string for the charity")
    donation_amount: int  # in cents

class TaskReport(BaseModel):
    routine_id: str = Field(..., description="MongoDB ObjectId string for the routine")
    did_task: bool

@app.post("/charity")
def add_charity(charity: CharityAdd):
    res = db.charities.insert_one({
        "name": charity.name,
        "stripe_account_id": charity.stripe_account_id
    })
    return {"message": "Charity added", "charity_id": str(res.inserted_id)}

@app.post("/routine")
def add_routine(r: RoutineAdd):
    if not ObjectId.is_valid(r.user_id):
        raise HTTPException(400, "Invalid user_id")
    if not db.users.find_one({"_id": ObjectId(r.user_id)}):
        raise HTTPException(404, f"user {r.user_id} not found")
    if not ObjectId.is_valid(r.charity_id):
        raise HTTPException(400, "Invalid charity_id")
    if not db.charities.find_one({"_id": ObjectId(r.charity_id)}):
        raise HTTPException(404, f"charity {r.charity_id} not found")

    res = db.routines.insert_one({
        "user_id": ObjectId(r.user_id),
        "description": r.description,
        "frequency": r.frequency,
        "charity_id": ObjectId(r.charity_id),
        "donation_amount": r.donation_amount,
        "did_task": False
    })
    return {"message": "Routine added", "routine_id": str(res.inserted_id)}

@app.post("/report-task")
def report_task(report: TaskReport):
    if not ObjectId.is_valid(report.routine_id):
        raise HTTPException(400, "Invalid routine_id")
    upd = db.routines.update_one(
        {"_id": ObjectId(report.routine_id)},
        {"$set": {"did_task": report.did_task}}
    )
    if upd.matched_count == 0:
        raise HTTPException(404, f"Routine {report.routine_id} not found")
    return {"message": f"Recorded did_task={report.did_task} for routine {report.routine_id}"}

def check_and_donate():
    for r in db.routines.find():
        if check_task(r):
            continue
        u = db.users.find_one({"_id": r["user_id"]})
        c = db.charities.find_one({"_id": r["charity_id"]})
        if not u or not c:
            continue
        try:
            print(f"[{r['frequency']}] Donated ${r['donation_amount']/100:.2f} "
                  f"from {u['email']} to {c['name']} for '{r['description']}'")
        except Exception as e:
            print(f"Error donating for routine {r['_id']}: {e}")
        db.routines.update_one({"_id": r["_id"]}, {"$set": {"did_task": False}})

def check_task(r):
    # TODO: implement your frequency logic
    return False

@app.post("/run-donations")
def run_donations(background_tasks: BackgroundTasks):
    background_tasks.add_task(check_and_donate)
    return {"message": "Donation check started in background"}
