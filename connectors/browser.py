import os

from selenium import webdriver

# TURN INTO CONFIG
DRIVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver")

def create_driver():
    return webdriver.Chrome(DRIVER_PATH)