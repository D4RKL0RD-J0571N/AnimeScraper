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

        for card in soup.select(".serie-card"):
            title_tag = card.select_one(".title h3 a")
            title = title_tag.text.strip() if title_tag else "Unknown Title"
            link = title_tag['href'] if title_tag else ""
            description = card.select_one(".serie-card__information p").text.strip()
            image_url = card.select_one(".image img")['src']
            year_tag = card.select_one(".tag.year")
            year = year_tag.text.strip() if year_tag else "Unknown Year"
            status_tag = card.select_one(".tag.airing")
            status = status_tag.text.strip() if status_tag else "Unknown Status"
            type_tag = card.select_one(".tag.type")
            anime_type = type_tag.text.strip() if type_tag else "Unknown Type"

            anime_list.append({
                "title": title,
                "link": link,
                "description": description,
                "image_url": image_url,
                "year": year,
                "status": status,
                "type": anime_type
            })

        return anime_list
