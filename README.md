# Anime Scraper

A Python project for scraping and downloading anime episodes from AnimeFenix, an anime streaming website. This project leverages web scraping techniques and Selenium to retrieve download links and handles downloading through multithreading for efficient processing.

## Features

- Scrapes anime episode links from AnimeFenix.
- Automatically retrieves the final download URLs using Selenium for websites that require JavaScript redirection.
- Downloads episodes concurrently using threading for improved efficiency.
- Customizable output directory for downloaded files.

## Requirements

- Python 3.6 or higher
- Libraries:
  - `requests`
  - `beautifulsoup4`
  - `tqdm`
  - `selenium`
  - `webdriver_manager` (optional, for automatically managing ChromeDriver)
  - `concurrent.futures`

You can install the required libraries using pip:

pip install requests beautifulsoup4 tqdm selenium webdriver_manager

## Setup

### Clone the repository:
```
git clone <repository_url>
cd <repository_directory>
```
Ensure you have Chrome installed. The project uses the Chrome browser for Selenium. You can download it from here.

Configure your environment: Update any necessary configurations in the code as needed.

## Usage

Running the Project

Import Necessary Modules:

Ensure you import the necessary modules in your main script:

```
from chapter_processor import ChapterProcessor
```
### Initialize the Processor:

Create an instance of the ChapterProcessor class with the required parameters:

```
session = <your_session>  # Replace with your session object
anime_link = "<anime_slug>"  # Slug of the anime (extracted from the URL)
anime_name = "<anime_name>"  # Name of the anime for file naming
chapter_processor = ChapterProcessor(session, anime_link, anime_name)
```

### Process Chapters:

Call the process_chapters method to start scraping and downloading:

```
start_chapter = 1  # Starting chapter number
end_chapter = 10   # Ending chapter number
output_dir = "downloads"  # Output directory for downloaded files
chapter_processor.process_chapters(start_chapter, end_chapter, output_dir)
```

## Example
Here's an example of how you might set everything up in a script:

```
from chapter_processor import ChapterProcessor

def main():
    session = <your_session>  # Your session handling code here
    anime_link = "youkai-gakkou-no-sensei-hajimemashita"  # Example slug
    anime_name = "Youkai Gakkou no Sensei Hajimemashita"
    
    chapter_processor = ChapterProcessor(session, anime_link, anime_name)
    start_chapter = 1
    end_chapter = 10
    output_dir = "downloads"
    
    chapter_processor.process_chapters(start_chapter, end_chapter, output_dir)

if __name__ == "__main__":
    main()
```
## Logging
The project uses Python's logging module to log important events, errors, and information. You can customize the logging configuration in your main script if needed.

## Troubleshooting
WebDriver Issues: If you encounter issues related to Selenium WebDriver, ensure you have the latest version of Chrome and that the webdriver_manager is correctly set up.

Access Denied Errors: If you face issues accessing the download page, check your session handling and ensure you are logged in.
# License
This project is licensed under the MIT License - see the LICENSE file for details.

### Acknowledgements
Beautiful Soup - For parsing HTML and XML documents.
Selenium - For automating web applications for testing purposes.
