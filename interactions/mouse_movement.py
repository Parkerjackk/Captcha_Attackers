import random
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

def nonLinear_mouse_movement(driver, start_x, start_y, target_x, target_y, steps = 50):
        
    ActionChains(driver).move_by_offset(0, 0).perform() # reset internal pointer

    ActionChains(driver).move_by_offset(start_x, start_y).perform() # move to random starting point

    action = ActionChains(driver)

    dx = (target_x - start_x) / steps
    dy = (target_y - start_y) / steps

    # Add noise to each step
    for _ in range(steps):
        noise_x = random.uniform(-1, 1)
        noise_y = random.uniform(-1, 1)
        action.move_by_offset(dx + noise_x, dy + noise_y).perform()
        # Add random speed
        time.sleep(random.uniform(0.01, 0.05))


def find_box(driver):
        
    # Cursor appears in random location on window - more human like
    window_size = driver.get_window_size()
    start_x = random.randint(0, window_size['width']-1)
    start_y = random.randint(0, window_size['height']-1)

    # Find text insert box
    box = driver.find_element(By.CSS_SELECTOR, ".captcha-input")
    
    # Get element center coordinates
    rect = box.rect
    target_x = rect['x'] + rect['width'] / 2
    target_y = rect['y'] + rect['height'] / 2

    # Move to the input box 
    nonLinear_mouse_movement(driver, start_x=start_x , start_y=start_y, target_x=target_x , target_y=target_y , steps = 50)
    ActionChains(driver).click().perform()

    return box, target_x, target_y

def validate(driver, start_x, start_y):

    # Find validate button
    validate = driver.find_element(By.CSS_SELECTOR, ".btn-primary")

    # Get element center coordinates
    rect = validate.rect
    target_x = rect['x'] + rect['width'] / 2
    target_y = rect['y'] + rect['height'] / 2

    # Move to the input box 
    nonLinear_mouse_movement(driver, start_x=start_x , start_y=start_y, target_x=target_x , target_y=target_y , steps = 50)
    ActionChains(driver).click().perform()