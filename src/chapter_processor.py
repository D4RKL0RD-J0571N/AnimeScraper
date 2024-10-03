import os
import random
import logging
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
from url_fetcher import URLFetcher
from downloader import Downloader
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class ChapterProcessor:
    def __init__(self, session, anime_link, anime_name):
        self.url_fetcher = URLFetcher()  # Initialize your URLFetcher
        self.url_fetcher.set_session(session)
        self.downloader = Downloader()
        self.anime_link = anime_link.split("/")[-1]  # Extract only the slug from the full URL
        self.anime_name = anime_name  # Store the anime name
        self.driver = self.setup_driver()  # Initialize Selenium WebDriver

    def setup_driver(self):
        """Sets up the Selenium WebDriver."""
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())  # Install and use ChromeDriver
        return webdriver.Chrome(service=service, options=options)

    def process_chapters(self, start_chapter, end_chapter, output_dir):
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        download_urls = []  # List to hold all download URLs

        for chapter in tqdm(range(start_chapter, end_chapter + 1), desc="Fetching URLs"):
            page_url = f"https://www3.animefenix.tv/ver/{self.anime_link}-{chapter}"  # Correct URL format
            download_page_url = f"{page_url}/descarga"  # Append "/descarga" for the download link page

            # Fetch the download page content
            download_page_content = self.url_fetcher.get_page_content(download_page_url)

            if download_page_content:
                # Parse the download page to find the preferred download link
                initial_url = self.get_download_link(download_page_content)

                if initial_url:
                    # Use Selenium to retrieve the final download link
                    final_download_url = self.get_final_download_url(initial_url)
                    if final_download_url:
                        download_urls.append(final_download_url)
                    else:
                        logging.warning(f"Failed to retrieve final download URL for chapter {chapter}")
                else:
                    logging.warning(f"Failed to fetch initial download URL for chapter {chapter}")
            else:
                logging.error(f"Failed to access download page for chapter {chapter}")

            time.sleep(random.uniform(1, 3))  # Sleep to avoid being blocked

        # Now download all the collected URLs concurrently
        if download_urls:
            self.downloader.download_files(download_urls, output_dir, self.anime_name)

        logging.info("All downloads initiated.")

    def get_final_download_url(self, initial_url):
        """Uses Selenium to open the initial URL and retrieve the final download link."""
        self.driver.get(initial_url)

        time.sleep(5)  # Wait for the page to load, adjust if necessary

        try:
            # Locate the download button or link
            download_button = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Descargar')]")  # Adjust if necessary
            download_button.click()

            # Wait for a while and retrieve the final URL
            time.sleep(5)  # Adjust based on the loading time for the download link
            final_url = self.driver.current_url

            logging.info(f"Final download URL retrieved: {final_url}")
            return final_url
        except Exception as e:
            logging.error(f"Failed to retrieve final download URL: {e}")
            return None

    def get_download_link(self, page_content):
        """Extracts download links from the page content and prioritizes servers like MediaFire."""
        soup = BeautifulSoup(page_content, 'html.parser')
        download_links = {}

        # Map server preferences (MediaFire first, then others)
        server_preferences = ["mediafire", "mega", "terabox", "1fichier", "fireload", "burstcloud"]

        # Find all download links
        for link in soup.find_all('a', class_='button is-fullwidth is-orange'):
            url = link['href']
            server_name = link.text.strip().lower()  # Extract server name (e.g., "mediafire", "mega")
            
            for server in server_preferences:
                if server in server_name:
                    download_links[server] = url
                    break  # Stop searching once the server is matched

        # Try preferred servers in the order defined in server_preferences
        for server in server_preferences:
            if server in download_links:
                logging.info(f"Selected download link from {server}: {download_links[server]}")
                return download_links[server]

        # If no preferred link was found
        logging.warning("No preferred download link found.")
        return None

    def __del__(self):
        """Close the WebDriver when the ChapterProcessor instance is deleted."""
        if self.driver:
            self.driver.quit()