import random
import time
import math

from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def humanlike_mouse_movement(driver, element, steps=12):

    # Use real viewport coordinates
    rect = driver.execute_script(
        "return arguments[0].getBoundingClientRect();",
        element
    )

    target_x = rect["left"] + rect["width"] / 2
    target_y = rect["top"] + rect["height"] / 2

    pointer = PointerInput("mouse", "mouse")
    actions = ActionBuilder(driver, mouse=pointer)

    # Move pointer to starting location (center of element)
    actions.pointer_action.move_to_location(int(target_x), int(target_y))
    actions.perform()


    for i in range(1, steps + 1):
        t = i / steps

        x = target_x + random.uniform(-1, 1)
        y = target_y + random.uniform(-1, 1)

        step_actions = ActionBuilder(driver, mouse=pointer)
        step_actions.pointer_action.move_to_location(int(x), int(y))
        step_actions.perform()

        delay = 0.015 + math.sin(t * math.pi) * 0.015
        time.sleep(delay)

    # Settle 
    time.sleep(0.05)


def humanlike_click(driver):

    pointer = PointerInput("mouse", "mouse")

    # Hesitate before click
    time.sleep(random.uniform(0.10, 0.20))

    # Press down
    down = ActionBuilder(driver, mouse=pointer)
    down.pointer_action.pointer_down()
    down.perform()

    time.sleep(random.uniform(0.05, 0.10))

    # Release
    up = ActionBuilder(driver, mouse=pointer)
    up.pointer_action.pointer_up()
    up.perform()

    time.sleep(0.10)


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