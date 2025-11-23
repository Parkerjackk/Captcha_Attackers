# tls_server.py

from fastapi import FastAPI
from pydantic import BaseModel
from async_tls_client import AsyncSession

from profiles.profile import BrowserProfile
from environment.cloud_selenium_wrapper import create_cloud_driver
from interactions.mouse_movement_cloud import find_box
from interactions.mouse_movement_cloud import validate

import random
import string

app = FastAPI()


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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/run_flow")
async def run_flow(profile: ProfileModel):
    """
    Full end-to-end flow:
    - TLS spoofing (using tls_client_name)
    - Launch spoofed Chrome
    - Load target page
    - Move mouse to box, type, click validate
    - Return summary
    """
    bp = BrowserProfile(**profile.dict())

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
        url = "https://group4.kokax.com/"
        driver.get(url)
        print(f"[Cloud] Loaded {url}")

        # Find input, move mouse, click
        box, bx, by = find_box(driver)

        # Type random character
        char = random.choice(string.ascii_letters)
        box.send_keys(char)

        # Click validate
        validate(driver, bx, by)

        return {
            "status": "ok",
            "char_used": char,
            "title": driver.title,
        }

    finally:
        driver.quit()
        print("[Cloud] Browser closed.")
