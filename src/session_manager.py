# session_manager.py
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import logging
import sys
import time
from webdriver_manager.chrome import ChromeDriverManager
from config import LOGIN_URL

class SessionManager:
    def __init__(self):
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

    def dynamic_log(self, message):
        sys.stdout.write(f"\r{message}")
        sys.stdout.flush()

    def is_captcha_present(self, driver):
        """Check if a CAPTCHA is present on the login page."""
        try:
            driver.find_element(By.CLASS_NAME, "g-recaptcha")
            return True
        except NoSuchElementException:
            return False

    def create_session(self, username, password):
        """Create a session with the specified username and password."""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")  # Run headless if no GUI is needed
        chrome_options.add_argument("--disable-gpu")

        # Use ChromeDriverManager to automatically manage the driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            driver.get(LOGIN_URL)
            self.dynamic_log("Navigating to login page...")

            # Wait and fill the login form
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)

            if self.is_captcha_present(driver):
                self.dynamic_log("CAPTCHA detected. Please solve the CAPTCHA in the browser and press Enter when done...")
                print("Solving the CAPTCHA...")  # Wait for user to solve CAPTCHA

            driver.find_element(By.ID, "send_button").click()
            self.logger.info("Clicked the login button.")
            time.sleep(3)  # Wait for login to process

            # Check for login success
            if "error" in driver.page_source:
                self.logger.error("Login failed due to incorrect credentials or CAPTCHA.")
                self.dynamic_log("Login failed. Check your credentials and CAPTCHA.")
                return None

            # Set session cookies
            cookies = driver.get_cookies()
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
            self.logger.info("Session cookies set successfully.")
            return self.session

        except (TimeoutException, WebDriverException) as e:
            self.logger.error(f"An error occurred during the login process: {e}")
            self.dynamic_log("An error occurred. Please check your internet connection or try again later.")
            return None

        finally:
            driver.quit()
            self.logger.info("WebDriver session closed.")
