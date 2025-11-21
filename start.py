# start.py

import asyncio
import random
import string

from profile_generator import generate_random_profile
from profile import BrowserProfile
from selenium_wrapper import create_selenium_driver
from tls_wrapper import create_tls_client
from mouse_movement import find_box
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


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
        # Go to Page
        driver.get("https://group4.kokax.com/")
        print("Browser launched and loaded https://example.com")

        # Match TLS & enforce WebGL injection
        tls_client = await create_tls_client(profile)
        print("TLS client initialized.")

        # Find the box & move to it
        box = find_box(driver)

        # Insert random character
        random_char = random.choice(string.ascii_letters)
        box.send_keys(random_char)

        # Wait so you can interact with the browser
        input("Press Enter to close the browser...")

    finally:
        driver.quit()
        print("Browser closed.")


if __name__ == "__main__":
    asyncio.run(main())
