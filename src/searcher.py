import requests
from bs4 import BeautifulSoup
import logging

class AnimeSearcher:
    BASE_SEARCH_URL = "https://www3.animefenix.tv/animes"

    def search_anime(self, anime_name=None, genres=None, years=None, types=None, statuses=None, order="default"):
        params = {}
        # If an anime name is provided, search only by name
        if anime_name:
            params['q'] = anime_name  # Use the 'q' parameter for name search
        else:
            # Otherwise, gather other search criteria
            if genres:
                params['genero[]'] = genres
            if years:
                params['year[]'] = years
            if types:
                params['type[]'] = types
            if statuses:
                params['estado[]'] = statuses
            params['order'] = order

        try:
            response = requests.get(self.BASE_SEARCH_URL, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            return self.parse_search_results(response.text)
        except requests.RequestException as e:
            logging.error(f"Error during anime search: {e}")
            return []

    def parse_search_results(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        anime_list = []

        # Loop through each anime card on the page, using a more general selector for cards
        for card in soup.select(".group.relative.overflow-hidden"):
            # Get title using a more generalized approach (e.g., 'alt' attribute of the image or text within 'h3')
            title_tag = card.select_one("h3")
            title = title_tag.text.strip() if title_tag else "Unknown Title"

            # Get link, ensuring fallback for href attributes
            link_tag = card.select_one("a")
            link = link_tag['href'] if link_tag else ""

            # Get image URL, prioritizing the 'src' attribute
            image_tag = card.select_one("img")
            image_url = image_tag['src'] if image_tag else ""

            # Get year, using a more generalized class or position-based selection
            year_tag = card.select_one("span.bg-primary")
            year = year_tag.text.strip() if year_tag else "Unknown Year"

            # Get status, using a more flexible selector
            status_tag = card.select_one("span.bg-zinc-700")
            status = status_tag.text.strip() if status_tag else "Unknown Status"

            # Append anime data to list
            anime_list.append({
                "title": title,
                "link": link,
                "image_url": image_url,
                "year": year,
                "status": status
            })

        return anime_list
