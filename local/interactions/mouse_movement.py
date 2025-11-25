import random
import time
import math
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def humanlike_mouse_movement(driver, element, steps=12):

    rect = element.rect
    target_x = rect["x"] + rect["width"] / 2
    target_y = rect["y"] + rect["height"] / 2

    pointer = PointerInput("mouse", "mouse")
    actions = ActionBuilder(driver, mouse=pointer)

    # Reset cursor to element center
    actions.pointer_action.move_to(element)
    actions.perform()

    # Random control points
    cp1 = (target_x + random.randint(-60, 60),
           target_y + random.randint(-60, 60))
    cp2 = (target_x + random.randint(-60, 60),
           target_y + random.randint(-60, 60))

    steps = 18

    for i in range(1, steps + 1):
        t = i / steps

        # Cubic Bézier easing
        x = ((1 - t)**3 * target_x +
             3 * (1 - t)**2 * t * cp1[0] +
             3 * (1 - t) * t**2 * cp2[0] +
             t**3 * target_x)

        y = ((1 - t)**3 * target_y +
             3 * (1 - t)**2 * t * cp1[1] +
             3 * (1 - t) * t**2 * cp2[1] +
             t**3 * target_y)

        # New action block each step
        step_actions = ActionBuilder(driver, mouse=pointer)
        step_actions.pointer_action.move_to_location(int(x), int(y))
        step_actions.perform()

        # Speed curve (slow → fast → slow)
        delay = 0.010 + math.sin(t * math.pi) * 0.025
        time.sleep(delay)

    # Settle jitter near target
    settle = ActionBuilder(driver, mouse=pointer)
    settle.pointer_action.move_by(1, 1)
    settle.perform()
    time.sleep(random.uniform(0.02, 0.05))

    time.sleep(random.uniform(0.05, 0.12))


def humanlike_click(driver):

    pointer = PointerInput("mouse", "mouse")

    # Hesitate before click
    time.sleep(random.uniform(0.12, 0.25))

    # Jitter
    jitter = ActionBuilder(driver, mouse=pointer)
    jitter.pointer_action.move_by(random.randint(-2, 2),
                                  random.randint(-2, 2))
    jitter.perform()
    time.sleep(random.uniform(0.05, 0.12))

    # Press down
    down = ActionBuilder(driver, mouse=pointer)
    down.pointer_action.pointer_down()
    down.perform()

    time.sleep(random.uniform(0.05, 0.10))

    # Release
    up = ActionBuilder(driver, mouse=pointer)
    up.pointer_action.pointer_up()
    up.perform()

    time.sleep(random.uniform(0.10, 0.20))


def find_box(driver):
    
    # Find text insert box
    box = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".captcha-input")))
    
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", box)
    time.sleep(0.2)

    # Move to the input box + click
    humanlike_mouse_movement(driver, box) 
    humanlike_click(driver)

    return box


def validate(driver):

    # Find validate button
    validate_btn = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".btn-primary")))

    # Scroll button into view
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", validate_btn)
    time.sleep(0.2)

    humanlike_mouse_movement(driver, validate_btn)
    humanlike_click(driver)