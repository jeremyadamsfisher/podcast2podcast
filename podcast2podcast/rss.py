from html.parser import HTMLParser
from io import StringIO
from typing import List, Tuple
from xml.sax.expatreader import SAXParseException

import requests
import untangle
from unidecode import unidecode


class TagStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    @classmethod
    def from_html(cls, html):
        s = cls()
        s.feed(html)
        return s.text.getvalue()


def parse_rss(rss_url: str) -> Tuple[str, List[Tuple[str, str]]]:
    """Parse an RSS feed.

    Args:
        rss_url (str): The RSS feed URL.

    Raises:
        ValueError: If the RSS feed could not be parsed.
        requests.exceptions.HTTPError: If the RSS feed could not be retrieved.

    Returns:
        Tuple[str, List[Tuple[str, str]]]: The podcast title and a list of episode titles and URLs.
    """
    resp = requests.get(rss_url)
    resp.raise_for_status()

    try:
        xml = untangle.parse(resp.content.decode())
        podcast_title = xml.rss.channel.title.cdata
        episodes = []
        for e in xml.rss.channel.item:
            title = unidecode(e.title.cdata)
            link = unidecode(e.link.cdata)
            episodes.append((title, link))
    except (SAXParseException, AttributeError):
        raise ValueError(f"Could not parse {rss_url}")

    return podcast_title, episodes


def get_podcast_details(rss_url: str, episode_idx: int) -> Tuple[str, str, str]:
    """Pull the relevant episode details from an RSS feed.

    Args:
        rss_url (str): The RSS feed URL.
        episode_idx (int): The episode index.

    Returns:
        PodcastEpisode: The episode details."""

    podcast_title, episodes = parse_rss(rss_url)
    episode_title, description = episodes[episode_idx]

    return podcast_title, episode_title, description
