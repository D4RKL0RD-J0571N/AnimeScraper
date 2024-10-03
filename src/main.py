from session_manager import SessionManager
from chapter_processor import ChapterProcessor
from searcher import AnimeSearcher
from logger import setup_logger
from config import get_output_dir
from episode_fetcher import EpisodeFetcher
import re  # Import regex for sanitization

def sanitize_filename(filename):
    """Replace illegal characters with underscores for directory names."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def main():
    setup_logger()
    
    # Initialize session manager and prompt for login credentials
    session_manager = SessionManager()
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # Create a session
    session = session_manager.create_session(username, password)
    if session:
        print("Login successful!")

        # Initialize the searcher
        searcher = AnimeSearcher()

        while True:
            print("\n--- Anime Search Menu ---")
            print("1. Search by Anime Name")
            print("2. Search by Filters")
            print("3. Exit")
            choice = input("Please choose an option (1-3): ")

            if choice == '1':
                # Search by Anime Name
                anime_name_input = input("Enter the anime name to search: ")
                results = searcher.search_anime(anime_name=anime_name_input)

            elif choice == '2':
                # Search by Filters
                genres_input = input("Enter genres (comma-separated): ")
                years_input = input("Enter years (comma-separated): ")
                statuses_input = input("Enter statuses (comma-separated, 1=Emisión, 2=Finalizado, etc.): ")

                # Parse inputs into lists
                genres = [genre.strip() for genre in genres_input.split(',')] if genres_input else None
                years = [year.strip() for year in years_input.split(',')] if years_input else None
                statuses = [status.strip() for status in statuses_input.split(',')] if statuses_input else None

                # Search for anime based on inputs
                results = searcher.search_anime(genres=genres, years=years, statuses=statuses)

            elif choice == '3':
                print("Exiting the program.")
                break

            else:
                print("Invalid choice, please try again.")
                continue

            # Display results
            if results:
                print("\nSearch Results:")
                for idx, anime in enumerate(results, start=1):
                    print(f"{idx}. {anime['title']} - {anime['year']} - {anime['status']}")
                    print(f"   Link: {anime['link']}")
                    print(f"   Description: {anime['description']}")
                    print(f"   Image: {anime['image_url']}\n")
                
                # Ask the user to select an anime by number
                choice = int(input("Select an anime by number to continue: ")) - 1
                if 0 <= choice < len(results):
                    selected_anime = results[choice]

                    # Set the original anime name and sanitize it for the output directory
                    anime_link = selected_anime['link']
                    anime_name = selected_anime['title']
                    sanitized_anime_name = sanitize_filename(anime_name.replace(" ", "-").lower())  # Sanitize the name for folder

                    # Create the output directory using the sanitized name
                    output_dir = get_output_dir(sanitized_anime_name)  # Use sanitized name here
                    
                    # Fetch episode links
                    episode_fetcher = EpisodeFetcher(session)
                    episode_links = episode_fetcher.fetch_episode_links(anime_name, anime_link)

                    # Display fetched episode links
                    if episode_links:
                        print("\nAvailable Episodes:")
                        for episode in episode_links:
                            print(f"{episode['title']}: {episode['url']}")

                        # Pass the base anime URL and anime name to the chapter processor
                        chapter_processor = ChapterProcessor(session, anime_link, anime_name)
                        chapter_processor.process_chapters(start_chapter=1, end_chapter=len(episode_links), output_dir=output_dir)  # Pass the output directory
                    else:
                        print("No episodes found.")
                else:
                    print("Invalid selection. Returning to menu...")
            else:
                print("No anime found with the specified criteria.")
    else:
        print("Session creation failed, terminating the script.")

if __name__ == "__main__":
    main()