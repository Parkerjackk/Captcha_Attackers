# start.py

import asyncio
import time
from pathlib import Path

from local.profiles.profile_generator import generate_random_profile
from local.profiles.profile import BrowserProfile
from local.environment.selenium_wrapper import create_selenium_driver
from local.environment.tls_wrapper import create_tls_client
from local.interactions.mouse_movement import find_box
from local.interactions.mouse_movement import validate
from local.get_captcha_views import download_captcha_views
from yolo.infer_session import infer_repeated_char


ROOT_DIR = Path(__file__).resolve().parents[1]
SESSION_VIEWS_DIR = ROOT_DIR / "temp"
WEIGHTS_PATH = ROOT_DIR / "yolo11s_model" / "weights" / "best.pt"


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

        # Allow the page to render
        time.sleep(0.05)

        # Download all captcha views into temp dir
        await download_captcha_views(driver, tls_client, SESSION_VIEWS_DIR)
        print(f"Saved views to {SESSION_VIEWS_DIR.resolve()}")
        
        # Find the box & move to it
        box= find_box(driver)

        # Infer repeated captcha char for the session
        answer_char, stats = infer_repeated_char(
            weights_path=str(WEIGHTS_PATH),
            session_dir=str(SESSION_VIEWS_DIR),
            imgsz=416,
            conf_th=0.6,
            device="cpu"
        )
        if answer_char is None:
            print("No detections: unable to infer answer.")
            return

        print("Per-class stats:")
        for c, s in sorted(stats.items(), key=lambda kv: kv[1]["total_dets"], reverse=True):
            print(
            f"  class {s['name']} (id {c}): "
            f"total_detections={s['total_dets']}, "
            f"images_where_appears_once={s['images_with_any']}, "
            f"images_where_appears_twice={s['images_with_two_plus']}"
            )

        box.send_keys(answer_char)

        # Validate Answer
        validate(driver)

        # Wait so you can interact with the browser
        input("Press Enter to close the browser...")

    finally:
        driver.quit()
        print("Browser closed.")


if __name__ == "__main__":
    asyncio.run(main())
