import os
import time
import base64
import json
import requests
import pyautogui
from pathlib import Path
from dotenv import load_dotenv

# -----------------------------------------------------------------
# 1. Load Environment (for API_KEY) and Set Constants
# -----------------------------------------------------------------
load_dotenv()  # Loads .env if present

API_KEY = os.getenv("API_KEY")
GPT_VISION_URL = "https://api.openai.com/v1/chat/completions"  # MUST be a vision-capable endpoint if you have it
MODEL_NAME = "gpt-4o-mini"  # Placeholder model name per docs

# Directory where we’ll store screenshots
SCREENSHOTS_DIR = "continuous_screenshots"
Path(SCREENSHOTS_DIR).mkdir(exist_ok=True)

# How long to capture screenshots in seconds
DURATION = 15
# How often to take a screenshot in seconds (e.g., every 2 seconds)
CAPTURE_INTERVAL = 1

# -----------------------------------------------------------------
# 2. Continuous Screenshots Function
# -----------------------------------------------------------------
def take_continuous_screenshots(
    screenshots_dir: str,
    duration: int = 15,
    interval: float = 1.0
):
    """
    Continuously captures screenshots for 'duration' seconds,
    saving each screenshot to 'screenshots_dir' every 'interval' seconds.
    """
    start_time = time.time()
    screenshot_count = 0

    print(f"Starting continuous screenshots for {duration} seconds...")

    while True:
        current_time = time.time()
        elapsed = current_time - start_time
        
        if elapsed > duration:
            break

        screenshot_path = Path(screenshots_dir) / f"screenshot_{screenshot_count:03d}.png"

        # Capture the entire screen
        image = pyautogui.screenshot()
        image.save(screenshot_path)
        print(f"Captured {screenshot_path}")

        screenshot_count += 1
        time.sleep(interval)  # Wait until next capture

    print(f"Captured a total of {screenshot_count} screenshots in '{screenshots_dir}'.")
    return screenshot_count

# -----------------------------------------------------------------
# 3. Encode Image Function (Base64)
# -----------------------------------------------------------------
def encode_image(image_path: str) -> str:
    """
    Reads an image from disk and returns a Base64-encoded string.
    """
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# -----------------------------------------------------------------
# 4. Analyze Screenshots with GPT-4 Vision in ONE request
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# 4. Analyze Screenshots with GPT-4 Vision in ONE request
# -----------------------------------------------------------------
def analyze_screenshots_with_gpt_vision(screenshots_dir: str) -> str:
    """
    Gathers all images in 'screenshots_dir', encodes them, and sends them
    in a single GPT-4 Vision request to generate one final SOP (not separate).
    """
    # Collect all PNG files in alphabetical order
    image_files = sorted(Path(screenshots_dir).glob("*.png"))
    if not image_files:
        return "No screenshots found to analyze."

    # Build the content array for the user message
    # We explicitly say: "Give me one final SOP" to ensure a consolidated response
    content_array = [
        {
            "type": "text",
            "text": (
                "Please look at all the images provided below, which show a screen recording session. "
                "I want you to create **one single, consolidated Standard Operating Procedure (SOP)** "
                "that covers the entire multi-step process depicted across **all** the screenshots. "
                "Do **not** create separate SOP sections for each image; instead, merge them into a "
                "single, cohesive SOP. Focus purely on the actions visible in the images and base "
                "your response solely on what can be inferred from these images. Provide numbered steps for the SOP"
            )
        }
    ]

    for img_path in image_files:
        base64_data = encode_image(str(img_path))
        content_array.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_data}"
                },
            }
        )

    # Now the 'messages' block uses the revised prompt
    messages = [
        {"role": "system", "content": "You are an AI expert in process automation. That analyses computed screenshots to come up with SOPs"},
        {
            "role": "user",
            "content": content_array,
        },
    ]

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 300,
        "temperature": 0.7,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    # Send the request
    try:
        response = requests.post(GPT_VISION_URL, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
            else:
                return "No content returned by GPT Vision."
        else:
            return f"Error {response.status_code}: {response.text}"

    except Exception as e:
        return f"Error connecting to GPT Vision: {e}"
# -----------------------------------------------------------------
# 5. Main: Continuous Capture, then One-Time Analysis
# -----------------------------------------------------------------
if __name__ == "__main__":
    # A. Continuously screenshot for DURATION seconds at CAPTURE_INTERVAL intervals
    num_screenshots = take_continuous_screenshots(
        SCREENSHOTS_DIR, 
        duration=DURATION,
        interval=CAPTURE_INTERVAL
    )

    if num_screenshots == 0:
        print("No screenshots captured. Exiting.")
        exit(0)

    # B. Analyze all captured screenshots with GPT-4 Vision
    print("\nAnalyzing all captured screenshots with GPT-4 Vision...")
    sop_result = analyze_screenshots_with_gpt_vision(SCREENSHOTS_DIR)

    print("\n=== Generated SOP/Analysis ===")
    print(sop_result)