import requests
from bs4 import BeautifulSoup
import logging
import threading
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import time

class URLFetcher:
    def __init__(self):
        self.session = None
        self.lock = threading.Lock()  # Ensure thread-safe logging and resource access
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def set_session(self, session):
        self.session = session

    def dynamic_log(self, message):
        """Log messages dynamically."""
        logging.info(message)

    def get_page_content(self, url):
        """Fetches the content of the specified URL using the session."""
        try:
            response = self.session.get(url) if self.session else requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            return response.text
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

    def get_final_url(self, start_url):
        """Get the final download URL from a given page."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            self.dynamic_log(f"Fetching URL: {start_url}")
            start_time = time.time()

            response = self.session.get(start_url, headers=headers)
            response.raise_for_status()

            elapsed_time = time.time() - start_time
            self.dynamic_log(f"Fetched {start_url} in {elapsed_time:.2f} seconds.")

            if "bot detection" in response.text.lower() or "captcha" in response.text.lower():
                self.dynamic_log("Request blocked due to bot detection or CAPTCHA.")
                return None

            soup = BeautifulSoup(response.content, 'html.parser')
            download_links = soup.find_all('a', class_='button', href=True)

            redirect_urls = [
                link['href'] for link in download_links 
                if 'redirect_download' in link['href'] and ('mediafire' in link.text.lower() or 'mega' in link.text.lower())
            ]

            if not redirect_urls:
                self.dynamic_log(f"No redirect download links found on the page: {start_url}")
                return None

            # Open the redirect URL in Selenium
            redirect_url = redirect_urls[0]
            self.dynamic_log(f"Opening redirect URL: {redirect_url}")
            options = Options()
            options.add_argument('--headless')  # Run in headless mode if needed
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get(redirect_url)

            # Wait for the download button to appear
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "downloadButton")))

            # Extract the actual download link
            try:
                download_button = driver.find_element(By.ID, "downloadButton")
                final_url = download_button.get_attribute("href")
                self.dynamic_log(f"Found final URL: {final_url}")
            except NoSuchElementException:
                logging.error("Download button not found. Page source: " + driver.page_source)
                self.dynamic_log("Error: Download button not found.")
                final_url = None

            # Close the WebDriver after use
            driver.quit()

            return final_url

        except requests.RequestException as e:
            logging.error(f"An error occurred while processing {start_url}: {e}")
            self.dynamic_log(f"Error occurred: {e}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            self.dynamic_log(f"Unexpected error occurred: {e}")
            return None

    def fetch_multiple_urls(self, start_urls):
        """
        This method handles multiple download pages concurrently using threads.
        """
        threads = []
        for url in start_urls:
            logging.debug(f"Fetching URL: {url}")  # Log the URL before fetching
            thread = threading.Thread(target=self.get_final_url, args=(url,))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        logging.info("All downloads processed.")

