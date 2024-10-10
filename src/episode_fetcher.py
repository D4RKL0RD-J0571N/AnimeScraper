import requests
from bs4 import BeautifulSoup
import logging

class EpisodeFetcher:
    def __init__(self, session):
        """Initialize the EpisodeFetcher with a session."""
        self.session = session
        self.episode_list_selector = 'ul.divide-y'  # Selector for the episode list
        self.episode_item_selector = 'li'  # Selector for episode items
        self.episode_link_selector = 'a'  # Selector for episode links

    def fetch_episode_links(self, anime_name, anime_link):
        """Fetch episode links for the specified anime."""
        print(f"Fetching episodes for: {anime_link}")  # Debugging statement
        try:
            response = self.session.get(anime_link)
            response.raise_for_status()  # Raise an error for bad responses
            
            soup = BeautifulSoup(response.content, 'html.parser')
            episode_list = soup.select_one(self.episode_list_selector)
            episode_links = []
            
            if episode_list:
                episodes = episode_list.select(self.episode_item_selector)
                for episode in episodes:
                    title_tag = episode.select_one(self.episode_link_selector)
                    if title_tag:
                        title = title_tag.text.strip()  # The text inside the <a> tag
                        link = title_tag['href']  # The href attribute contains the episode URL
                        
                        # Extract the episode number, handling the "Visto" case
                        try:
                            # Extract the episode number, ignoring any additional text (like "Visto")
                            episode_number = int(title.split("Episodio")[-1].strip().split()[0])  # Get the first part before any extra text
                        except ValueError:
                            logging.warning(f"Could not parse episode number from title: {title}. Skipping this episode.")
                            continue  # Skip this episode if parsing fails

                        episode_links.append({'title': title, 'url': link, 'number': episode_number})
                    else:
                        logging.warning(f"Episode element without an anchor tag found in {anime_name}. Skipping.")
            else:
                logging.warning(f"Episode list not found for {anime_name} at {anime_link}. Page structure may have changed.")
                print(f"Episode list not found for {anime_name} at {anime_link}")  # Debugging statement

            if not episode_links:
                logging.warning(f"No episodes found for {anime_name} at {anime_link}.")
                print(f"No episodes found for {anime_name} at {anime_link}")  # Debugging statement

            # Sort episodes by episode number before returning
            episode_links.sort(key=lambda ep: ep['number'])

            return episode_links

        except requests.RequestException as e:
            logging.error(f"Failed to fetch episodes for {anime_name}. Error: {e}")
            return []

        except Exception as e:
            logging.error(f"Unexpected error occurred while fetching episodes for {anime_name}. Error: {e}")
            return []
