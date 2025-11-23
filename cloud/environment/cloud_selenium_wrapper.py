# cloud_selenium_wrapper.py
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from environment.webgl_spoof_cloud import build_webgl_spoof_script_cloud
from environment.canvas_spoof_cloud import build_canvas_spoof_script
from environment.audio_spoof_cloud import build_audio_spoof_script
from environment.navigator_spoof_cloud import build_navigator_spoof_script

def create_cloud_driver(profile):

    # ---- Chrome options ----
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--disable-gpu")

    # UA spoof
    chrome_opts.add_argument(f"--user-agent={profile.user_agent}")

    # Language + locale spoof
    chrome_opts.add_argument(f"--lang={profile.language}")

    # Timezone spoof via environment variable
    os.environ["TZ"] = profile.timezone

    # ---- Launch Chrome ----
    driver = webdriver.Chrome(options=chrome_opts)

    # ---- Apply viewport ----
    w, h = profile.viewport
    driver.set_window_size(w, h)

    # ---- Inject spoofing scripts ----

    scripts = [
        build_webgl_spoof_script_cloud(profile),
        build_canvas_spoof_script(profile),
        build_audio_spoof_script(profile),
        build_navigator_spoof_script(profile)
    ]

    for script in scripts:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": script}
        )

    return driver
