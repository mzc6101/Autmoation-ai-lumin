import mss
import numpy as np
import time
from pathlib import Path
import requests
import json
import cv2

# ---------------------------------------
# Configuration
# ---------------------------------------
OLLAMA_URL = "http://localhost:11400/api/generate"  # Ollama API endpoint
MODEL_NAME = "moondream:latest"  # Ollama model name
FRAMES_DIR = "frames"  # Directory to save screenshots
DURATION = 10  # Duration in seconds for screen capturing
CAPTURE_INTERVAL = 1  # Interval in seconds between screenshots

# ---------------------------------------
# Function to Capture Multiple Screenshots
# ---------------------------------------
def capture_screenshots(duration, interval, output_dir="frames"):
    Path(output_dir).mkdir(exist_ok=True)
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor
        width = monitor["width"]
        height = monitor["height"]
        print(f"Screen resolution detected: {width}x{height}")
        print(f"Starting screenshot capture for {duration} seconds at {interval}-second intervals...")
        
        start_time = time.time()
        elapsed = 0
        count = 0
        
        while elapsed < duration:
            img = sct.grab(monitor)
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            timestamp = int(elapsed)
            frame_path = Path(output_dir) / f"frame_{count:03d}.jpg"
            cv2.imwrite(str(frame_path), frame)
            print(f"Captured {frame_path}")
            count += 1
            time.sleep(interval)
            elapsed = time.time() - start_time
        
        print(f"Captured {count} screenshots to '{output_dir}' directory.")
        return count

# ---------------------------------------
# Analyze Screenshots with Ollama
# ---------------------------------------
def analyze_screenshots_with_ollama(output_dir="frames"):
    frame_files = sorted(Path(output_dir).glob("*.jpg"))
    frame_count = len(frame_files)
    
    if frame_count == 0:
        print("No screenshots to analyze.")
        return "No screenshots were captured for analysis."
    
    # Describe the screenshots as interactions on the HTML page
    frame_descriptions = []
    for frame_path in frame_files:
        frame_descriptions.append(
            f"Frame {frame_path.name}: The user interacts with the provided HTML demo page, potentially toggling info sections, clicking buttons, or copying text."
        )
    
    combined_description = "\n".join(frame_descriptions)
    prompt = (
        "You are an expert in workflow automation. Based on the following user interactions captured "
        "from screenshots of the provided HTML page (show/hide info, copy text, etc.), "
        "identify repetitive or time-consuming tasks and suggest actionable automation opportunities.\n\n"
        f"{combined_description}\n\n"
        "Provide detailed, practical recommendations as a numbered list."
    )
    
    payload = {"model": MODEL_NAME, "prompt": prompt}
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True)
        if response.status_code == 200:
            # Ollama may send the response in chunks
            analysis = ""
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    try:
                        data = json.loads(line)
                        analysis += data.get("data", "")
                    except json.JSONDecodeError:
                        # Handle lines that are not JSON
                        analysis += line
            analysis = analysis.strip()
            if not analysis:
                analysis = "No data returned by Ollama."
            return analysis
        else:
            return f"Error from Ollama API: {response.text}"
    except Exception as e:
        return f"Error connecting to Ollama API: {e}"

# ---------------------------------------
# Main Execution Flow
# ---------------------------------------
if __name__ == "__main__":
    # Step 1: Capture multiple screenshots
    captured_frames = capture_screenshots(DURATION, CAPTURE_INTERVAL, FRAMES_DIR)
    
    # Step 2: Analyze captured screenshots with Ollama
    if captured_frames > 0:
        print("Analyzing screenshots with Ollama...")
        analysis_results = analyze_screenshots_with_ollama(FRAMES_DIR)
        print("\nAutomation Recommendations:")
        print(analysis_results)
    else:
        print("No screenshots captured; skipping analysis.")