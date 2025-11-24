# mouse_movement_cloud.py

import random
import time
from selenium.webdriver.common.by import By


def cdp_move(driver, x, y):
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mouseMoved",
        "x": int(x),
        "y": int(y),
    })


def cdp_click(driver, x, y):
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mousePressed",
        "x": int(x),
        "y": int(y),
        "button": "left"
    })
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mouseReleased",
        "x": int(x),
        "y": int(y),
        "button": "left"
    })


def move_smooth(driver, sx, sy, tx, ty, steps=50):
    dx = (tx - sx) / steps
    dy = (ty - sy) / steps
    x, y = sx, sy

    for _ in range(steps):
        x += dx + random.uniform(-1, 1)
        y += dy + random.uniform(-1, 1)
        cdp_move(driver, x, y)
        time.sleep(random.uniform(0.01, 0.05))


def find_box(driver):
    metrics = driver.execute_cdp_cmd("Page.getLayoutMetrics", {})
    width = metrics["layoutViewport"]["clientWidth"]
    height = metrics["layoutViewport"]["clientHeight"]

    start_x = random.randint(0, width - 1)
    start_y = random.randint(0, height - 1)

    box = driver.find_element(By.CSS_SELECTOR, ".captcha-input")
    rect = box.rect

    tx = rect['x'] + rect['width'] / 2
    ty = rect['y'] + rect['height'] / 2

    move_smooth(driver, start_x, start_y, tx, ty)
    cdp_click(driver, tx, ty)
    return box, tx, ty


def validate(driver, bx, by):
    # Find the validate button
    btn = driver.find_element(By.CSS_SELECTOR, ".btn-primary")

    # Try to find the enclosing form
    try:
        form = btn.find_element(By.XPATH, "./ancestor::form")
        print("[Cloud] Found parent form, submitting via JS")

        # Scroll it into view for visuals (optional)
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior:'auto',block:'center'});",
            btn
        )
        time.sleep(0.2)

        # Submit the form directly
        driver.execute_script("arguments[0].submit();", form)
    except Exception as e:
        print("[Cloud] Could not find/submit form:", e)
        # Fallback: just click via JS
        driver.execute_script("arguments[0].click();", btn)
        print("[Cloud] Clicked validate via JS .click() fallback")

    # Give the page time to show the result
    time.sleep(1.0)
