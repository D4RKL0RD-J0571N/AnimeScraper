# config.py
LOGIN_URL = "https://www3.animefenix.tv/user/login"
BASE_SEARCH_URL = "https://www3.animefenix.tv/animes"

# Function to get the output directory based on the anime name
def get_output_dir(anime_name):
    return f"d:/Series/{anime_name}"