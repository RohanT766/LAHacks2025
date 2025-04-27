#!/usr/bin/env python3
import os
import sys
import json
import base64
from typing import Optional

from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
from google.generativeai import GenerativeModel, configure

# ───────────────────────────────────────────────────────────
# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_USER     = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST     = os.getenv("MONGO_HOST")
DB_NAME        = os.getenv("DB_NAME")

# ───────────────────────────────────────────────────────────
# Gemini setup
configure(api_key=GEMINI_API_KEY)
gemini = GenerativeModel("gemini-2.0-flash")

# ───────────────────────────────────────────────────────────
# MongoDB setup
MONGO_URI        = (
    f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}"
    f"/{DB_NAME}?retryWrites=true&w=majority"
)
mongo_client     = MongoClient(MONGO_URI)
tasks_collection = mongo_client[DB_NAME].tasks  # assumes a `tasks` collection

# ───────────────────────────────────────────────────────────
def validate_task_image(user_id: str, image_path: str) -> bool:
    """
    Given a user_id and a local image file path, ask Gemini
    if this image legitimately shows the user's pending task completed.
    Returns True if yes, False otherwise.
    """
    # Load the user's current pending task
    task = tasks_collection.find_one({
        "user_id": ObjectId(user_id),
        "status": "pending"
    })
    if not task:
        raise ValueError(f"No pending task found for user {user_id}")

    task_desc = task.get("description", "the assigned task")

    # Read and Base64-encode image
    with open(image_path, "rb") as f:
        raw_bytes = f.read()
    b64_str = base64.b64encode(raw_bytes).decode("utf-8")
    data_uri = f"data:image/jpeg;base64,{b64_str}"

    # Build and send the multimodal prompt
    prompt = (
        f"I have a user-assigned task: “{task_desc}”.\n"
        "Attached is a photo the user submitted to prove completion.\n"
        "Does this image clearly and accurately show that the task is complete?\n"
        "Answer only “YES” or “NO”."
    )

    response = gemini.generate_content(
        messages=[{"role": "user", "content": prompt}],
        embed=[{"type": "image_base64", "data": data_uri}],
        temperature=0.0,
        max_tokens=3
    )

    answer = response.choices[0].message["content"].strip().upper()

    # 4) Interpret the response
    is_complete = answer.startswith("YES")

    # 5) Update task status in DB
    new_status = "complete" if is_complete else "failed"
    tasks_collection.update_one(
        {"_id": task["_id"]},
        {"$set": {"status": new_status}}
    )

    return is_complete

# ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 task_image_validator.py <user_id> <image_path>")
        sys.exit(1)

    user_id, img_path = sys.argv[1], sys.argv[2]
    ok = validate_task_image(user_id, img_path)
    print(f"Task verification result: {'✅ COMPLETED' if ok else '❌ FAILED'}")
