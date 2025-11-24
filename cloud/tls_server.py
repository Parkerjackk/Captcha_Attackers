# tls_server.py

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from async_tls_client import AsyncSession

from profiles.profile import BrowserProfile
from environment.cloud_selenium_wrapper import create_cloud_driver
from interactions.mouse_movement_cloud import find_box
from interactions.mouse_movement_cloud import validate

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import random
import string
import uuid
import os
import time

app = FastAPI()

SCREENSHOT_DIR = "/tmp/screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

class ProfileModel(BaseModel):
    name: str
    version: str
    os: str
    hardware_type: str
    user_agent: str
    language: str
    timezone: str
    viewport: tuple
    webgl_vendor: str
    webgl_renderer: str
    canvas_seed: int
    audio_seed: int
    tls_client_name: str
    proxy: str | None = None


def save_screenshot(driver, label: str) -> str:
    unique_id = str(uuid.uuid4())
    filename = f"{label}_{unique_id}.png"
    full_path = os.path.join(SCREENSHOT_DIR, filename)
    
    driver.save_screenshot(full_path)
    print(f"[Cloud] Saved screenshot: {full_path}")

    return f"/screenshot/{filename}"
    

def wait_for_results(driver):
    """
    Wait for Captcha result msg and return
    """
    try: 
        msg = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".message"))
        )

        text = msg.text.strip()

        classes = msg.get_attribute("class")

        if "success" in classes:
            return {"type": "success", "text": text}
        
        elif "error" in classes:
            return {"type": "error", "text": text}
        
        elif "info" in classes:
            return {"type": "info", "text": text}

        else:
            return {"type": "unknown", "text": text}
    
    except Exception:
        return {"type": "none_detected", "text": "No result message appeared"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/screenshot/{filename}")
def get_screenshot(filename: str):
    full_path = os.path.join(SCREENSHOT_DIR, filename)
    if not os.path.exists(full_path):
        return {"error" : "screenshot not found"}
    
    return FileResponse(full_path)


@app.post("/run_flow")
async def run_flow(profile: ProfileModel):
    """
    Full end-to-end flow:
    - TLS spoofing (using tls_client_name)
    - Launch spoofed Chrome
    - Load target page
    - Move mouse to box, type, click validate
    - Scan text and return it
    - Return screenshots URLs of each step
    """
    bp = BrowserProfile(**profile.model_dump())

    print("\n[Cloud] Running flow with profile:")
    for k, v in bp.__dict__.items():
        print(f"{k}: {v}")
    print("=================================\n")

    # --- TLS spoofing (AsyncSession with tls_client_name) ---
    session = AsyncSession(client_identifier=bp.tls_client_name)
    async with session:
        # Cheap handshake to apply fingerprint
        await session.get("https://example.com")
    print("[Cloud] TLS fingerprint applied.")

    # --- Spoofed Selenium driver in the cloud ---
    driver = create_cloud_driver(bp)
    print("[Cloud] Browser launched with spoofed profile.")

    try:
        driver.get("https://group4.kokax.com/")
        print(f"[Cloud] Loaded https://group4.kokax.com/")

        url_loaded = save_screenshot(driver, "loaded")
        
        # Find input box, move mouse, click
        box, bx, by = find_box(driver)

        # Type random character
        char = random.choice(string.ascii_letters)
        box.send_keys(char)

        url_typed = save_screenshot(driver, "typed")

        # Click validate
        validate(driver, bx, by)

        url_validated = save_screenshot(driver, "validated")
        time.sleep(1.0)
        
        # Scan result value
        result = wait_for_results(driver)
        print(f"[Cloud] CAPTCHA Result:", result)

        url_result = save_screenshot(driver, "result")


        return {
            "status": "ok",
            "char_used": char,
            "title": driver.title,
            "captcha_result": result,
            "screenshots": {
                "loaded": url_loaded,
                "typed": url_typed,
                "validated": url_validated,
                "result": url_result
            }
        }

    finally:
        driver.quit()
        print("[Cloud] Browser closed.")
