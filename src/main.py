import re
import logging
from session_manager import SessionManager
from chapter_processor import ChapterProcessor
from searcher import AnimeSearcher
from logger import setup_logger
from config import get_output_dir
from episode_fetcher import EpisodeFetcher
from config import SERVER_PREFERENCES
from config import XPATH
# Import server preferences


class AnimeDownloader:
    def __init__(self):
        setup_logger()
        self.logger = logging.getLogger(__name__)
        self.session_manager = SessionManager()
        self.searcher = AnimeSearcher()
        self.session = None

    def sanitize_filename(self, filename):
        """Replace illegal characters with underscores for directory names."""
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    def prompt_login(self):
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        self.session = self.session_manager.create_session(username, password)
        if not self.session:
            print("Failed to create session. Check your credentials or network connection.")
            self.logger.error("Session creation failed.")
            return False
        print("Login successful!")
        self.logger.info("Login successful.")
        return True

    def search_anime(self):
        while True:
            print("\n--- Anime Search Menu ---")
            print("1. Search by Anime Name")
            print("2. Search by Filters")
            print("3. Exit")
            choice = input("Please choose an option (1-3): ")

            if choice == '1':
                anime_name_input = input("Enter the anime name to search: ")
                results = self.searcher.search_anime(anime_name=anime_name_input)
            elif choice == '2':
                results = self.search_with_filters()
            elif choice == '3':
                print("Exiting the program.")
                self.logger.info("Program exited by user.")
                break
            else:
                print("Invalid choice, please try again.")
                continue

            self.handle_results(results)

    def search_with_filters(self):
        genres_input = input("Enter genres (comma-separated): ")
        years_input = input("Enter years (comma-separated): ")
        statuses_input = input("Enter statuses (comma-separated, 1=Emisión, 2=Finalizado, etc.): ")

        genres = [genre.strip() for genre in genres_input.split(',')] if genres_input else None
        years = [year.strip() for year in years_input.split(',')] if years_input else None
        valid_statuses = {"1": "Emisión", "2": "Finalizado", "3": "Proximamente", "4": "En Cuarentena"}
        statuses = [status.strip() for status in statuses_input.split(',') if status.strip() in valid_statuses]

        self.logger.info(f"Searching anime with filters: genres={genres}, years={years}, statuses={statuses}")
        return self.searcher.search_anime(genres=genres, years=years, statuses=statuses)

    def handle_results(self, results):
        if results:
            print("\nSearch Results:")
            for idx, anime in enumerate(results, start=1):
                print(f"{idx}. {anime['title']} - {anime.get('year', 'N/A')} - {anime.get('status', 'N/A')}")
                print(f"   Link: {anime.get('link', 'N/A')}")
                print(f"   Description: {anime.get('description', 'No description available.')}")

            choice = self.select_anime(results)
            if choice is not None:
                self.process_anime(choice)
        else:
            print("No results found. Please try a different search.")
            self.logger.warning("No results found during the search.")

    def select_anime(self, results):
        try:
            choice = int(input("Select an anime by number to continue: ")) - 1
            if not (0 <= choice < len(results)):
                raise ValueError("Invalid selection, please try again.")
            return results[choice]
        except ValueError as ve:
            print(f"Error: {ve}")
            self.logger.error(f"Invalid selection: {ve}")
            return None

    def process_anime(self, selected_anime):
        anime_link = selected_anime['link']
        anime_name = selected_anime['title']
        sanitized_anime_name = self.sanitize_filename(anime_name.replace(" ", "-").lower())
        output_dir = get_output_dir(sanitized_anime_name)

        episode_fetcher = EpisodeFetcher(self.session)
        episode_links = episode_fetcher.fetch_episode_links(anime_name, anime_link)

        if episode_links:
            print("\nAvailable Episodes:")
            for idx, episode in enumerate(episode_links, start=1):
                print(f"{idx}. {episode['title']} - {episode['url']}")

            start_chapter, end_chapter = self.prompt_chapter_range()
            config = {
            "server_preferences": SERVER_PREFERENCES,
            "download_button_xpath": XPATH,  # Add your actual XPath here
            }
            if start_chapter is not None and end_chapter is not None:
                chapter_processor = ChapterProcessor(self.session, anime_link, anime_name, config) #Here goes the config
                chapter_processor.process_chapters(start_chapter, end_chapter, output_dir)

                self.logger.info(f"Processed chapters from {start_chapter} to {end_chapter} for {anime_name}.")
        else:
            print("No episodes found for the selected anime.")
            self.logger.warning(f"No episodes found for {anime_name}.")

    def prompt_chapter_range(self):
        while True:
            try:
                start_chapter = int(input("Enter the start chapter number: "))
                end_chapter = int(input("Enter the end chapter number: "))
                if start_chapter < 1 or end_chapter < start_chapter:
                    print("Invalid range. Ensure start chapter is less than or equal to end chapter, and both are positive.")
                    self.logger.error("Invalid chapter range provided.")
                    continue
                return start_chapter, end_chapter
            except ValueError:
                print("Invalid input. Please enter numeric values for chapter numbers.")
                self.logger.error("Invalid input for chapter numbers.")

def main():
    downloader = AnimeDownloader()
    if downloader.prompt_login():
        downloader.search_anime()

if __name__ == "__main__":
    main()
