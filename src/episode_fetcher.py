import requests
from bs4 import BeautifulSoup
import logging

class EpisodeFetcher:
    def __init__(self, session):
        """Initialize the EpisodeFetcher with a session."""
        self.session = session

    def fetch_episode_links(self, anime_name, anime_link):
        """Fetch episode links for the specified anime."""
        print(f"Fetching episodes for: {anime_link}")  # Debugging statement
        try:
            response = self.session.get(anime_link)
            response.raise_for_status()  # Raise an error for bad responses
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # Locate the episode list using the class 'anime-page__episode-list'
            episode_list = soup.find('ul', class_='anime-page__episode-list')

            episode_links = []
            if episode_list:
                # Find all episode entries within the list
                episodes = episode_list.find_all('li')
                for episode in episodes:
                    title_tag = episode.find('a')
                    if title_tag:
                        title = title_tag.text.strip()  # The text inside the <a> tag
                        link = title_tag['href']  # The href attribute contains the episode URL
                        episode_links.append({'title': title, 'url': link})
                    else:
                        logging.warning(f"Episode element without an anchor tag found in {anime_name}. Skipping.")

            if not episode_links:
                logging.warning(f"No episodes found for {anime_name} at {anime_link}.")
                print(f"No episodes found for {anime_name} at {anime_link}")  # Debugging statement

            return episode_links

        except requests.RequestException as e:
            logging.error(f"Failed to fetch episodes for {anime_name}. Error: {e}")
            return []
