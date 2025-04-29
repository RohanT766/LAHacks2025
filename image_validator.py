#!/usr/bin/env python3
import os
import base64
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
from google.generativeai import GenerativeModel, configure
from fastapi import HTTPException
import certifi
import traceback

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DBNAME = os.getenv("MONGO_DB", "lahacks25")

# Configure Gemini
configure(api_key=GEMINI_API_KEY)
gemini = GenerativeModel("gemini-1.5-flash")

# Set up MongoDB
client: MongoClient[Any] = MongoClient(MONGO_URL, tls=True, tlsCAFile=certifi.where())
db: Any = client[MONGO_DBNAME]

def validate_task_image(task_description: str, image_data: str) -> bool:
    """
    Validates if an image shows task completion using Gemini API.
    
    Args:
        task_description: The description of the task to verify
        image_data: Base64 encoded image data (with data URI prefix)
        
    Returns:
        bool: True if the image shows task completion, False otherwise
        
    Raises:
        HTTPException: If there's an error processing the image
    """
    try:
        print(f"\n=== Starting Image Validation ===")
        print(f"Task Description: {task_description}")
        
        # Decode base64 image
        try:
            print("Decoding base64 image...")
            header, b64 = image_data.split(",", 1)
            data = base64.b64decode(b64)
            print("Base64 image decoded successfully")
        except Exception as e:
            print(f"Error decoding base64 image: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(400, f"Invalid image format: {str(e)}")
        
        # Prepare the prompt
        prompt = f"""
        Task Description: "{task_description}"
        
        Please analyze this image and determine if it clearly shows the completion of the task.
        Consider:
        1. Does the image show the expected outcome of the task?
        2. Is the image clear and unambiguous?
        3. Does it match the task description?
        
        Answer only "YES" if the image clearly shows task completion, or "NO" if it doesn't.
        """
        
        print("Sending request to Gemini API...")
        try:
            # Generate content with Gemini
            response = gemini.generate_content(
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": b64
                                }
                            }
                        ]
                    }
                ],
                generation_config={
                    "temperature": 0.0,
                    "max_output_tokens": 3,
                    "top_p": 1,
                    "top_k": 1
                }
            )
            print("Received response from Gemini API")
            
            # Parse the response
            if not response:
                print("Empty response from Gemini API")
                raise HTTPException(500, "No response from Gemini API")
            
            if not hasattr(response, 'text'):
                print("Response has no text attribute")
                print(f"Response object: {response}")
                raise HTTPException(500, "Invalid response format from Gemini API")
            
            answer = response.text.strip().upper()
            print(f"Gemini API response: {answer}")
            
            is_valid = answer.startswith("YES")
            print(f"Validation result: {'valid' if is_valid else 'invalid'}")
            print("=== Image Validation Complete ===\n")
            
            return is_valid
            
        except Exception as e:
            print(f"Error in Gemini API call: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(500, f"Error processing image with Gemini: {str(e)}")
        
    except HTTPException as he:
        print(f"HTTP Exception: {he.detail}")
        raise he
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Error processing image: {str(e)}")


# Allow standalone testing:
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python3 image_validator.py <user_id> <image_path>")
        sys.exit(1)

    uid, img = sys.argv[1], sys.argv[2]
    res = validate_task_image(uid, img)
    print("✅ COMPLETED" if res else "❌ FAILED")
