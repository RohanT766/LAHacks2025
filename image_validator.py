#!/usr/bin/env python3
import os
import base64
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
from google.generativeai import GenerativeModel, configure
from fastapi import HTTPException

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_USER     = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST     = os.getenv("MONGO_HOST")
DB_NAME        = os.getenv("DB_NAME")

# Set up Gemini
configure(api_key=GEMINI_API_KEY)
gemini = GenerativeModel("gemini-2.0-flash")

# Set up MongoDB
MONGO_URI        = (
    f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}"
    f"/{DB_NAME}?retryWrites=true&w=majority"
)
mongo_client     = MongoClient(MONGO_URI)
tasks_collection = mongo_client[DB_NAME].tasks

def validate_task_image(user_id: str, image_path: str) -> bool:
    """
    Returns True if Gemini determines the image proves the user's pending task is complete.
    Raises HTTPException on errors.
    """
    # 1) Load the user's pending task
    task = tasks_collection.find_one({
        "user_id": ObjectId(user_id),
        "status": "pending"
    })
    if not task:
        raise HTTPException(404, f"No pending task for user {user_id}")

    task_desc = task.get("description", "the assigned task")

    # 2) Read & Base64-encode the image
    try:
        raw = open(image_path, "rb").read()
        b64 = base64.b64encode(raw).decode("utf-8")
    except Exception as e:
        raise HTTPException(400, f"Failed to read image: {e}")

    data_uri = f"data:image/jpeg;base64,{b64}"

    # 3) Query Gemini
    prompt = (
        f"I have a user-assigned task: “{task_desc}”.\n"
        "Attached is a photo the user submitted to prove completion.\n"
        "Does this image clearly and accurately show that the task is complete?\n"
        "Answer only “YES” or “NO”."
    )
    resp = gemini.generate_content(
        messages=[{"role": "user", "content": prompt}],
        embed=[{"type": "image_base64", "data": data_uri}],
        temperature=0.0,
        max_tokens=3
    )
    answer = resp.choices[0].message["content"].strip().upper()
    is_complete = answer.startswith("YES")

    # 4) Update task status
    new_status = "complete" if is_complete else "failed"
    tasks_collection.update_one(
        {"_id": task["_id"]},
        {"$set": {"status": new_status}}
    )

    return is_complete


# Allow standalone testing:
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python3 image_validator.py <user_id> <image_path>")
        sys.exit(1)

    uid, img = sys.argv[1], sys.argv[2]
    res = validate_task_image(uid, img)
    print("✅ COMPLETED" if res else "❌ FAILED")
