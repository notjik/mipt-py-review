import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from config import WEBDRIVER_PATH

def make_driver():
    return webdriver.Chrome(service=Service(WEBDRIVER_PATH), options=get_options())


def get_options():
    options = webdriver.ChromeOptions()
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    ]
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("window-size=1920,1080")
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    return options


def emulate_user(driver):
    time.sleep(3)
    body = driver.find_element(By.TAG_NAME, 'body')
    for _ in range(random.randint(3, 5)):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(random.uniform(1, 3))