# session_manager.py
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import logging
import sys
import time
from webdriver_manager.chrome import ChromeDriverManager

from config import LOGIN_URL

class SessionManager:
    def __init__(self):
        self.session = requests.Session()

    def dynamic_log(self, message):
        sys.stdout.write(f"\r{message}")
        sys.stdout.flush()

    def is_captcha_present(self, driver):
        try:
            driver.find_element(By.CLASS_NAME, "g-recaptcha")
            return True
        except NoSuchElementException:
            return False

    def create_session(self, username, password):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Use ChromeDriverManager to automatically manage the driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            driver.get(LOGIN_URL)
            self.dynamic_log("Navigating to login page...")

            # Wait and fill the login form
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)

            if self.is_captcha_present(driver):
                self.dynamic_log("CAPTCHA detected. Please solve the CAPTCHA in the browser and press Enter when done...")
                time.sleep(3)

            driver.find_element(By.ID, "send_button").click()
            logging.info("Clicked the login button.")
            time.sleep(3)  # Wait for login to process

            if "error" in driver.page_source:
                logging.error("Login failed.")
                self.dynamic_log("Login failed. Check your credentials and CAPTCHA.")
                return None

            cookies = driver.get_cookies()
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
            logging.info("Session cookies set.")
            return self.session

        finally:
            driver.quit()
            logging.info("WebDriver session closed.")
