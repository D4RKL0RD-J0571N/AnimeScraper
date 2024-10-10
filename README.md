# Anime Scraper

Anime Scraper is a Python application for downloading episodes and chapters of anime from the AnimeFenix website. It allows users to log in, search for their favorite anime, and fetch episodes or chapters with ease.

## Features

- User authentication with session management.
- Search anime by name or apply filters (genres, years, statuses).
- Fetch and download episodes and chapters from preferred servers.
- Configurable server preferences for download links.
- Logging for tracking progress and errors.

## Requirements

- Python 3.6 or higher
- Libraries:
  - `requests`
  - `beautifulsoup4`
  - `tqdm`
  - `selenium`
  - `webdriver_manager`

You can install the required libraries using pip:
```
pip install requests beautifulsoup4 tqdm selenium webdriver_manager
```

## Setup

### Clone the Repository:

```
git clone https://github.com/D4RKL0RD-J0571N/AnimeScraper.git
cd AnimeScraper
```


### Run the Application:

To start the application, execute the main.py script:

```
python main.py
```
### Login:

Enter your username and password when prompted.

### Search for Anime:

- Choose to search by anime name or filters.

- Select an anime from the search results to proceed.

### Download Episodes:

- Choose the range of chapters you want to download.
- The application will process and download the chapters to your specified output directory.

## Usage

### Key Classes
- AnimeDownloader: Main class that handles user input and coordinates the download process.
- SessionManager: Manages user sessions for login and maintaining authenticated states.
- AnimeSearcher: Handles searching for anime based on user input.
- EpisodeFetcher: Fetches episode links for the selected anime.
- ChapterProcessor: Processes and downloads chapters using Selenium to navigate to the final download URLs.


Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## Logging
The project uses Python's logging module to log important events, errors, and information. You can customize the logging configuration in your main script if needed.

## Troubleshooting
WebDriver Issues: If you encounter issues related to Selenium WebDriver, ensure you have the latest version of Chrome and that the webdriver_manager is correctly set up.
-Access Denied Errors: If you face issues accessing the download page, check your session handling and ensure you are logged in.
- 403 Forbidden client error response status code indicates that the server understood the request but refused to process it, this is caused by authentication protocols like Captchas.

# License
This project is licensed under the GNU License - see the LICENSE file for details.
