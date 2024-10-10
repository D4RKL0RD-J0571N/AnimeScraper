import os
import requests
from tqdm import tqdm
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

class Downloader:
    def download_file(self, download_url, output_dir, anime_name, episode_number=None, retries=3):
        """Download a file from the given URL to the specified output directory."""
        # Extract file name from the URL
        file_name = os.path.basename(download_url)

        # Construct a cleaner file name if an episode number is provided
        if episode_number is not None:
            clean_episode_number = f"{int(episode_number):02}"
            file_name = f"{anime_name} - Episode {clean_episode_number}.mp4"

        file_path = os.path.join(output_dir, file_name)

        # Skip download if the file already exists
        if os.path.exists(file_path):
            logging.info(f"File already exists, skipping: {file_name}")
            return file_path

        # Attempt to download the file
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()  # Raise error for bad responses

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            total_size = int(response.headers.get('content-length', 0))
            with open(file_path, 'wb') as file:
                # Use tqdm for progress indication if total size is known
                with tqdm(
                    desc=file_name,
                    total=total_size if total_size else None,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar:
                    for data in response.iter_content(chunk_size=1024):
                        file.write(data)
                        bar.update(len(data))

            # Check if the download was incomplete
            if total_size and os.path.getsize(file_path) < total_size and retries > 0:
                logging.warning(f"Incomplete download for {file_name}, retrying...")
                return self.download_file(download_url, output_dir, anime_name, episode_number, retries - 1)

            logging.info(f"File downloaded successfully: {file_path}")
            return file_path

        except requests.ConnectionError as ce:
            logging.error(f"Connection error while downloading {file_name}. Error: {ce}")
        except requests.Timeout as te:
            logging.error(f"Timeout error while downloading {file_name}. Error: {te}")
        except requests.HTTPError as he:
            logging.error(f"HTTP error {response.status_code} while downloading {file_name}. Error: {he}")
        

    def download_files(self, download_urls, output_dir, anime_name):
        """Download multiple files concurrently."""
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust max_workers as needed
            future_to_url = {executor.submit(self.download_file, url, output_dir, anime_name): url for url in download_urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logging.error(f"Error downloading {url}: {e}")
        return results