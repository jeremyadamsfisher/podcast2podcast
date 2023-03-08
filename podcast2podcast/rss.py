from dataclasses import dataclass
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
            description = TagStripper.from_html(unidecode(e.description.cdata))
            episodes.append(title, description)
    except (SAXParseException, AttributeError):
        raise ValueError(f"Could not parse {rss_url}")

    return podcast_title, episodes
