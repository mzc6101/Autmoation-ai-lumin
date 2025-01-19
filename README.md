**README: Screen Recorder with GPT-4 Vision SOP Generation and Automation**

_This is a Python script (screen_recorder_with_ai.py) that:_

1.	Continuously captures screenshots for a specified duration.
2.	Sends all captured screenshots to a GPT‑4o-mini Vision–capable endpoint.
3.	Generates a consolidated Standard Operating Procedure (SOP) based purely on the visual information in the screenshots.
Additionally, there is an HTML test page to demonstrate repetitive user actions (like clicking a “Show Info” button or copying text repeatedly) which can then be analyzed by GPT-4 Vision or Ollama API with a vision LLM like meta's Lamma. Our code here is set up for GPT as you can try it yourself very easily.

_Overview:_

1.	The HTML test page (Test Page for Screen Recording.html in the example) prompts you to perform repetitive tasks.
2.	The Python script screen_recorder_with_ai.py uses pyautogui to take screenshots on an interval.
3.	After the capturing period, the script sends the screenshots as base64-encoded images to a GPT-4 Vision endpoint.
4.	GPT-4 Vision then analyzes these images and generates a single SOP describing what was done on screen.
_Prerequisites:_

•	Python 3.7+
•	A GPT-4 Vision–capable API endpoint (i.e., access to GPT-4 Vision). Or Ollama API endpoint with a vision LLM
•	Basic knowledge of terminal/command-line usage.
•	(Optional) A local HTTP server to serve the HTML test page if you want to replicate the exact environment.
Find out more on: https://ollama.com/ for details on how to set up ollama on your local device.

_How It Works:_

1.	Screenshot Capture
•	The script captures continuous screenshots for DURATION seconds.
•	You can configure the capture interval (CAPTURE_INTERVAL) in seconds.
2.	Frame Collection & Encoding
•	Once capturing ends, the script collects all .png images from the continuous_screenshots folder.
•	Each image is base64-encoded.
3.	GPT-4 Vision Request
•	The script sends a single request to the GPT Vision endpoint.
•	All images are included in one user message, using the documented {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."} } structure.
4.	SOP Generation
•	GPT-4 Vision returns a text response describing or analyzing the series of screenshots.
•	The script prints out the final SOP in the terminal.
Setup and Running

Install Dependencies
Clone this repository (or download the script) and install the necessary Python packages:

    pip install --upgrade pip
    pip install requests pyautogui python-dotenv
• requests to make POST calls to the API. • pyautogui for screenshot functionality. • python-dotenv to manage environment variables (API Key).

Note: Mac users may need to grant screen capture permissions to Python in System Preferences → Security & Privacy → Screen Recording. 

_2. Set Your API Key_

In your project folder, create a file named .env (if not already present) and add your API Key:

    API_KEY=sk-XXXXXXXXXXXXXXXXXXX
Alternatively, you can export your API key in your shell environment:

    export API_KEY=sk-XXXXXXXXXXXXXXXXXXX
_3. Run the HTML Test Page (Optional)_

Open Test Page for Screen Recording.html (or the snippet from the question) in your browser. Perform some repetitive actions like: • Clicking the “Show Info” / “Hide Info” button multiple times. • Copying text via the “Copy Text” button.

These actions will be captured in screenshots.

Alternatively, you can do any other on-screen tasks you want to analyze.

_4. Run the Python Script_

Run:

python3 screen_recorder_with_ai.py
• The script will say: “Starting continuous screenshots for 15 seconds…” • It will take a screenshot every 1 second by default (both durations are configurable). • Once finished, it prints “Analyzing all captured screenshots with GPT-4o-mini Vision…” and sends them to your GPT-4 Vision endpoint.

Resulting SOP/Analysis

When the script completes, it prints the SOP or analysis returned by GPT-4 Vision. For example:

=== Generated SOP/Analysis ===

Standard Operating Procedure (SOP) for Test HTML
This final text is based exclusively on what GPT-4 Vision “sees” in the screenshots. image

Notes on GPT-4 Vision Access • If you do not have Vision access, you may see a response like “I apologize, but I cannot view images.” • To confirm Vision availability, check your account or docs.

Work in Progress: AppleScript Automation Generator

Below is a Work In Progress Script (automation_generator.py) to show how you might use the GPT-4 Vision SOP to automatically craft an AppleScript (or similar) that replicates the steps identified in the SOP. This is not a fully working script; it’s a blueprint of how you could proceed after receiving the SOP.

    #!/usr/bin/env python3
    """
    Work-In-Progress script to convert a GPT-4 Vision SOP into an AppleScript
    that automates the same actions described by the SOP.
    """

    import subprocess

    def convert_sop_to_applescript(sop_text: str) -> str:
    """
    Takes SOP text as input (e.g., steps for opening a browser,
    clicking a button, copying text) and generates an AppleScript
    that attempts to replicate these actions.

    This is a simplified example:
    1. You might parse each step from the SOP.
    2. For each step, decide what AppleScript command can replicate it.
    """
    # NOTE: This example is placeholder logic
    lines = sop_text.split("\n")
    applescript_lines = [
        'tell application "System Events"',
        'activate'
    ]
    
    for line in lines:
        # Hypothetically detect words like 'click', 'copy', etc.
        if "click" in line.lower():
            # Example AppleScript that might move & click at coordinates
            # Actual coordinates would be gleaned from your screen layout or stored mappings
            applescript_lines.append('    click at {100, 200}')
        if "open browser" in line.lower():
            # AppleScript to open Safari or Chrome
            applescript_lines.append('    tell application "Safari" to activate')
        if "copy" in line.lower():
            # Key command for copy
            applescript_lines.append('    keystroke "c" using command down')
    
    applescript_lines.append("end tell")
    
    return "\n".join(applescript_lines)
    
    def generate_and_run_applescript(sop_text: str):
    """
    Generates the AppleScript from the SOP and executes it on macOS.
    """
    script_content = convert_sop_to_applescript(sop_text)
    
    # Write the AppleScript to a temporary .applescript file
    script_file = "generated_actions.applescript"
    with open(script_file, "w") as f:
        f.write(script_content)
    
    # Then call 'osascript' to run it
    subprocess.run(["osascript", script_file])
    print(f"AppleScript executed. Content was:\n\n{script_content}")
    
    if __name__ == "__main__":
    # Hypothetical text coming from GPT-4 Vision
    example_sop = """
    1. Open a web browser and go to the test page.
    2. Click the "Show Info" button.
    3. Click the "Copy Text" button to copy repeated text.
    4. Toggle "Hide Info" after done copying.
    """
    # Generate & run an AppleScript
    generate_and_run_applescript(example_sop)
Explanation:

• convert_sop_to_applescript(): Parses the SOP text and attempts to match each step to a relevant AppleScript command (very simplistic in this example). • generate_and_run_applescript(): Writes out the AppleScript to a temporary file and executes it via osascript. • Future enhancements: • Map actual UI elements to screen coordinates or better yet, use AppleScript’s GUI scripting by referencing buttons by name in a known app. • Incorporate dynamic screen dimensions for clicks. • Customize logic for each step (click, copy, open new tab, etc.).

Conclusion

• Use screen_recorder_with_ai.py to capture screenshots and generate a final SOP via GPT‑4 Vision. • Then feed that SOP (which outlines the repetitive steps) into your AppleScript generator script to automate those steps.

This approach transforms a visual screen capture → GPT-4 Vision SOP → automation script, closing the loop between observation and automated workflows.
