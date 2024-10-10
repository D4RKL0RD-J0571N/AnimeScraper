import requests
from bs4 import BeautifulSoup
import logging
import threading
from selenium.webdriver.support import expected_conditions as EC

class URLFetcher:
    def __init__(self, config=None):
        self.session = None
        self.lock = threading.Lock()  # Ensure thread-safe logging and resource access
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.config = config or {
            "download_button_id": "downloadButton",
            "link_class": "bg-orange-500",  # Adjust based on class used in the HTML
            "redirect_download_keyword": "redirect_download"
        }

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
            response = self.session.get(start_url, headers=headers)
            response.raise_for_status()

            if "bot detection" in response.text.lower() or "captcha" in response.text.lower():
                self.dynamic_log("Request blocked due to bot detection or CAPTCHA.")
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the download link directly by ID
            try:
                download_button = soup.find('a', id=self.config["download_button_id"])
                if download_button and download_button['href']:
                    final_url = download_button['href']
                    self.dynamic_log(f"Found final URL: {final_url}")
                    return final_url
                else:
                    self.dynamic_log("Download button not found or does not contain a link.")
                    return None
            except Exception as e:
                logging.error(f"Error finding the download button: {e}")
                return None

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
