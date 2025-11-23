# start.py

import asyncio
import random
import string
import argparse

from profiles.profile_generator import generate_random_profile
from profiles.profile import BrowserProfile
from environment.selenium_wrapper import create_selenium_driver
from environment.tls_wrapper import create_tls_client
from interactions.mouse_movement import find_box
from interactions.mouse_movement import validate



async def main():

    # Generate a new identity
    raw_profile = generate_random_profile()
    profile = BrowserProfile(**raw_profile)

    # Display BOT realistic characteristics
    print("\n=== Starting browser with profile ===")
    for k, v in profile.__dict__.items():
        print(f"{k}: {v}")
    print("====================================\n")

    # Launch Selenium
    driver = create_selenium_driver(profile)

    try:
        # Load Page
        driver.get("https://group4.kokax.com/")
        print("Browser launched and loaded https://group4.kokax.com/")

        # Match TLS & enforce WebGL injection
        tls_client = await create_tls_client(profile)
        print("TLS client initialized.")

        # Find the box & move to it
        box, box_x, box_y = find_box(driver)

        # Insert random character
        random_char = random.choice(string.ascii_letters)
        box.send_keys(random_char)

        # Validate Answer
        validate(driver, box_x, box_y)

        # Wait so you can interact with the browser
        input("Press Enter to close the browser...")

    finally:
        driver.quit()
        print("Browser closed.")


if __name__ == "__main__":
    asyncio.run(main())
