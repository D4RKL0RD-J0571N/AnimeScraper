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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException



class ChapterProcessor:
    def __init__(self, session, anime_link, anime_name, config):
        self.url_fetcher = URLFetcher()  # Initialize your URLFetcher
        self.url_fetcher.set_session(session)
        self.downloader = Downloader()  # Use the existing Downloader class
        self.anime_link = anime_link.split("/")[-1]  # Extract only the slug from the full URL
        self.anime_name = anime_name  # Store the anime name
        self.driver = None  # Initialize as None
        self.config = config  # Store configuration
        self.setup_driver()  # Initialize Selenium WebDriver
        

    def setup_driver(self):
        """Sets up the Selenium WebDriver."""
        options = webdriver.ChromeOptions()
        #options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-popup-blocking")

        service = Service(ChromeDriverManager().install())  # Install and use ChromeDriver
        self.driver = webdriver.Chrome(service=service, options=options)

    def process_chapters(self, start_chapter, end_chapter, output_dir):
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        download_urls = []  # List to hold all download URLs

        for chapter in tqdm(range(start_chapter, end_chapter + 1), desc="Fetching URLs"):
            page_url = self.construct_page_url(chapter)
            download_page_url = f"{page_url}/descarga"  # Append "/descarga" for the download link page

            # Fetch the download page content with error handling
            try:
                html_content = self.url_fetcher.get_page_content(download_page_url)
            except Exception as e:
                logging.error(f"Failed to fetch download page content for chapter {chapter}: {e}")
                continue  # Skip to the next chapter

            if html_content:
                # Parse the download page to find the preferred download link
                initial_url = self.get_download_link(html_content)

                if initial_url:
                    # Use Selenium to retrieve the final download link with retry handling
                    final_download_url = self.get_final_download_url(initial_url)
                    if final_download_url:
                        download_urls.append(final_download_url)
                        logging.info(f"Chapter {chapter} processing complete.")
                    else:
                        logging.warning(f"Failed to retrieve final download URL for chapter {chapter}")
                else:
                    logging.warning(f"Failed to fetch initial download URL for chapter {chapter}")
            else:
                logging.error(f"Failed to access download page for chapter {chapter}")

            time.sleep(random.uniform(1, 3))  # Sleep to avoid being blocked

        # Now download all the collected URLs using the Downloader class
        if download_urls:
            self.downloader.download_files(download_urls, output_dir, self.anime_name)
            logging.info("All downloads initiated.")

    def construct_page_url(self, chapter):
        """Constructs the page URL dynamically."""
        return f"https://www3.animefenix.tv/ver/{self.anime_link}-{chapter}"

    def get_download_link(self, page_content):
        """Extracts download links from the page content and prioritizes servers based on config."""
        soup = BeautifulSoup(page_content, 'html.parser')
        download_links = {}

        # Find all download links in the 'space-y-4' section
        links_section = soup.find('div', class_='max-w-4xl')  # Adjust based on your actual HTML structure
        if links_section:
            for link in links_section.find_all('a', href=True):
                url = link['href']
                server_name = link.text.strip().lower()  # Get server name from link text

                # Check if the server name is in the preferences
                for server in self.config["server_preferences"]:
                    if server in server_name:
                        download_links[server] = url
                        break  # Stop searching once the server is matched

        # Try preferred servers in the order defined in server_preferences
        for server in self.config["server_preferences"]:
            if server in download_links:
                logging.info(f"Selected download link from {server}: {download_links[server]}")
                return download_links[server]

        # If no preferred link was found
        logging.warning("No preferred download link found.")
        return None

    def get_final_download_url(self, initial_url, max_retries=3, wait_time=5):
        """Uses Selenium to open the initial URL and retrieve the final download link with retries."""
        self.driver.get(initial_url)
        logging.info(f"Opening URL: {initial_url}")

        # Retry mechanism
        for attempt in range(max_retries):
            try:
                # Get current window handle
                original_window = self.driver.current_window_handle

                # Switch to the new tab
                for window_handle in self.driver.window_handles:
                    if window_handle != original_window:
                        self.driver.switch_to.window(window_handle)
                        logging.info(f"Switched to new tab, current URL: {self.driver.current_url}")
                        break

                # Wait for the final URL to load
                WebDriverWait(self.driver, wait_time).until(EC.url_changes(initial_url))
                final_url = self.driver.current_url  # Retrieve the current URL after the redirect
                logging.info(f"Final download URL retrieved: {final_url}")
                
                try:
                    download_button = self.driver.find_element(By.ID, "downloadButton")
                    final_url = download_button.get_attribute("href")
                    logging.info(f"Found final URL: {final_url}")
                    return final_url
                except NoSuchElementException:
                    logging.error("Download button not found on attempt " + str(attempt + 1))
                    logging.error("Download button not found. Page source: " + self.driver.page_source)

            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(wait_time)  # Wait before retrying

        logging.error(f"Failed to retrieve final download URL after {max_retries} attempts.")
        return None

    def __del__(self):
        """Close the WebDriver when the ChapterProcessor instance is deleted."""
        if self.driver:
            self.driver.quit()
