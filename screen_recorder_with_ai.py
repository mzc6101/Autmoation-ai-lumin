import os
import time
import base64
import json
import requests
import pyautogui
from pathlib import Path
from dotenv import load_dotenv
from pynput import keyboard

# -----------------------------------------------------------------
# 1. Load Environment 
# -----------------------------------------------------------------
load_dotenv()  # Loads .env if present

API_KEY = os.getenv("API_KEY")
GPT_VISION_URL = "https://api.openai.com/v1/chat/completions"  # Adjust if you have a specialized Vision endpoint
MODEL_NAME = "gpt-4o-mini"  # Placeholder model name per docs

# Directory where we’ll store screenshots + keystrokes
SCREENSHOTS_DIR = "continuous_screenshots"
Path(SCREENSHOTS_DIR).mkdir(exist_ok=True)

# How long to capture screenshots (and keystrokes) in seconds
DURATION = 15
# How often to take a screenshot in seconds 
CAPTURE_INTERVAL = 1

# -----------------------------------------------------------------
# 2. Utility to Encode Image 
# -----------------------------------------------------------------
def encode_image(image_path: str) -> str:
    """
    Reads an image from disk and returns a Base64-encoded string.
    """
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# -----------------------------------------------------------------
# 3. Keystroke Logger 
# -----------------------------------------------------------------
class KeystrokeLogger:
    """
    Logs keystrokes to a text file with timestamps 
    relative to a reference start_time.
    """
    def __init__(self, log_dir: str):
        self.log_path = Path(log_dir) / "keystrokes.txt"
        self.start_time = None
        self.listener = None

    def on_press(self, key):
        try:
            # Attempt to capture the key character if it exists
            if hasattr(key, 'char') and key.char is not None:
                key_str = key.char  # e.g. 'a', 'b', '1', etc.
            else:
                # Special keys: e.g., Key.enter, Key.shift
                # We'll log them in brackets, e.g. [ENTER]
                key_str = f"[{key.name.upper()}]"

            elapsed = time.time() - self.start_time

            # Append keystroke with timestamp to the file
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"{elapsed:.2f}s: {key_str}\n")

        except Exception as e:
            print(f"Error logging key: {e}")

    def start(self):
        """
        Starts the key-logging listener in a background (daemon) thread.
        """
        self.start_time = time.time()
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.daemon = True  # Ends when main thread ends
        self.listener.start()

    def stop(self):
        """
        Gracefully stops the key-logging listener.
        """
        if self.listener:
            self.listener.stop()
            self.listener = None

# -----------------------------------------------------------------
# 4. Continuous Screenshots + Keystroke Capture
# -----------------------------------------------------------------
def take_continuous_screenshots(
    screenshots_dir: str,
    duration: int = 15,
    interval: float = 1.0
):
    """
    Continuously captures screenshots for 'duration' seconds,
    saving each screenshot to 'screenshots_dir' every 'interval' seconds,
    while simultaneously logging keystrokes to a text file.
    """
    start_time = time.time()
    screenshot_count = 0

    # Initialize and start keystroke logging
    keystroke_logger = KeystrokeLogger(screenshots_dir)
    keystroke_logger.start()

    print(f"Starting continuous capture for {duration} seconds (screenshots + keystrokes)...")

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

        # Sleep for 'interval' seconds, but subtract any overhead that just happened
        time.sleep(max(0, interval - (time.time() - current_time)))

    # Stop keystroke logging
    keystroke_logger.stop()

    print(f"Captured {screenshot_count} screenshots and keystrokes in '{screenshots_dir}'.")
    return screenshot_count

# -----------------------------------------------------------------
# 5. Analyze Screenshots (and Keystrokes) with GPT-4 Vision
# -----------------------------------------------------------------
def analyze_screenshots_with_gpt_vision(screenshots_dir: str) -> str:
    """
    Gathers all images + keystroke logs, 
    and sends them to GPT-4 Vision to generate a single SOP.
    """
    # Collect all PNG files in alphabetical order
    image_files = sorted(Path(screenshots_dir).glob("*.png"))
    keystroke_file = Path(screenshots_dir) / "keystrokes.txt"

    # If no screenshots, no point analyzing
    if not image_files:
        return "No screenshots found to analyze."

    # -----------------------------------------------------------
    # Build the user content with both text (keystrokes) + images
    # -----------------------------------------------------------
    content_array = [
        {
            "type": "text",
            "text": (
                "Below, you'll see a combined record of a screen session and the corresponding keystrokes. "
                "Use these to produce a **single, consolidated Standard Operating Procedure (SOP)**. "
                "Incorporate both the visual actions and the typed inputs into numbered steps. "
                "Focus only on what can be inferred from the screenshots + keystrokes, "
                "and do not create separate sections for each screenshot. Combine everything "
                "into one cohesive procedure.\n\n"
                "=== Keystroke Log ===\n"
            ),
        }
    ]

    # Append keystroke log (if any)
    if keystroke_file.exists():
        with open(keystroke_file, "r", encoding="utf-8") as f:
            keystrokes = f.read()
        content_array[0]["text"] += keystrokes
    else:
        content_array[0]["text"] += "No keystrokes recorded.\n"

    # Now add images to the content array
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

    # Create messages for Chat Completion
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI with advanced vision capabilities. "
                "You can see what is happening in the screenshots and read keystroke logs. "
                "Synthesize them into a single Standard Operating Procedure."
            )
        },
        {
            "role": "user",
            "content": content_array,
        },
    ]

    # Prepare the payload for GPT-4 Vision
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 500,      # Adjust as needed
        "temperature": 0.7,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    # Send the request to GPT-4 Vision
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
# 6. Main Flow
# -----------------------------------------------------------------
if __name__ == "__main__":
    # A. Continuously capture screenshots and keystrokes for DURATION seconds
    num_screenshots = take_continuous_screenshots(
        SCREENSHOTS_DIR, 
        duration=DURATION,
        interval=CAPTURE_INTERVAL
    )

    if num_screenshots == 0:
        print("No screenshots captured. Exiting.")
        exit(0)

    # B. Analyze all captured screenshots + keystrokes with GPT-4 Vision
    print("\nAnalyzing all captured screenshots + keystrokes with GPT-4 Vision...")
    sop_result = analyze_screenshots_with_gpt_vision(SCREENSHOTS_DIR)

    print("\n=== Generated SOP/Analysis ===")
    print(sop_result)