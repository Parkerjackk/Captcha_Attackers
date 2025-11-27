# mouse_movement_cloud.py

import random
import time
import math
from selenium.webdriver.common.by import By

# ---- Chrome DevTools Protocol (CDP) used due to use of headless Chrome ----

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
        "button": "left",
        "clickCount": 1
    })
    time.sleep(random.uniform(0.03, 0.10))

    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mouseReleased",
        "x": int(x),
        "y": int(y),
        "button": "left",
        "clickCount": 1
    })


def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return (
        (u ** 3) * p0 +
        (3 * u * u * t) * p1 +
        (3 * u * t * t) * p2 +
        (t ** 3) * p3
    )


def human_curve_motion(driver, sx, sy, tx, ty):


    # Distance to target affects speed
    dist = math.dist((sx, sy), (tx, ty))

    # Determine step count from distance (longer = more steps)
    steps = int(max(25, min(120, dist / 4)))

    # Control points create a subtle curve
    cp1 = (sx + (tx - sx) * 0.3 + random.uniform(-60, 60),
           sy + (ty - sy) * 0.3 + random.uniform(-60, 60))

    cp2 = (sx + (tx - sx) * 0.6 + random.uniform(-60, 60),
           sy + (ty - sy) * 0.6 + random.uniform(-60, 60))

    # Optional overshoot
    overshoot_strength = random.uniform(5, 18)
    tx_overshoot = tx + random.uniform(-overshoot_strength, overshoot_strength)
    ty_overshoot = ty + random.uniform(-overshoot_strength, overshoot_strength)

    # Execute full movement
    for i in range(1, steps + 1):
        t = i / steps

        # Smooth acceleration → fast middle → slow end
        ease = math.sin((t * math.pi) / 2)

        x = bezier(sx, cp1[0], cp2[0], tx_overshoot, ease)
        y = bezier(sy, cp1[1], cp2[1], ty_overshoot, ease)

        cdp_move(driver, x, y)

        # Delay also scales with distance
        base_delay = max(0.002, min(0.012, dist / 6000))
        jitter_delay = random.uniform(0, 0.003)
        time.sleep(base_delay + jitter_delay)

    # Minor settle at exact target
    cdp_move(driver, tx, ty)
    time.sleep(random.uniform(0.02, 0.05))


def find_box(driver):
    metrics = driver.execute_cdp_cmd("Page.getLayoutMetrics", {})
    width = metrics["layoutViewport"]["clientWidth"]
    height = metrics["layoutViewport"]["clientHeight"]

    sx = random.randint(0, width - 1)
    sy = random.randint(0, height - 1)

    box = driver.find_element(By.CSS_SELECTOR, ".captcha-input")
    rect = box.rect

    tx = rect['x'] + rect['width'] / 2
    ty = rect['y'] + rect['height'] / 2

    human_curve_motion(driver, sx, sy, tx, ty)
    cdp_click(driver, tx, ty)
    return box, tx, ty


def validate(driver, bx, by):
    # Find the validate button
    btn = driver.find_element(By.CSS_SELECTOR, ".btn-primary")

    rect = btn.rect
    tx = rect['x'] + rect['width'] / 2
    ty = rect['y'] + rect['height'] / 2

    
    metrics = driver.execute_cdp_cmd("Page.getLayoutMetrics", {})
    sx = metrics["layoutViewport"]["clientWidth"] / 2
    sy = metrics["layoutViewport"]["clientHeight"] / 2

    human_curve_motion(driver, sx, sy, tx, ty)
    cdp_click(driver, tx, ty)

    # Give the page time to show the result
    time.sleep(0.3)
