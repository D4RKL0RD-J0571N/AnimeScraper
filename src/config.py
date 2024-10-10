# config.py
LOGIN_URL = "https://www3.animefenix.tv/user/login"
BASE_SEARCH_URL = "https://www3.animefenix.tv/animes"

# Add server preferences here
SERVER_PREFERENCES = ["mediafire", "mega", "1ficher"]  # Replace with actual server names

XPATH = "//a[contains(@href, 'redirect_download.php')]"

# Function to get the output directory based on the anime name
def get_output_dir(anime_name):
    return f"d:/Series/{anime_name}"