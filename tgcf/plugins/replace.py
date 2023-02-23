import logging
from typing import Any, Dict
import requests
from urllib.parse import urlparse, parse_qs

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from tgcf.plugin_models import Replace
from tgcf.plugins import TgcfMessage, TgcfPlugin
from tgcf.utils import replace


class TgcfReplace(TgcfPlugin):
    id_ = "replace"

    def __init__(self, data):
        self.replace = data
        logging.info(self.replace)

    def modify(self, tm: TgcfMessage) -> TgcfMessage:
        msg_text: str = tm.text
        if not msg_text:
            return tm
        for original, new in self.replace.text.items():
            msg_text = replace(original, new, msg_text, self.replace.regex)

        # Check for links in message text
        links = self.find_links(msg_text)

        for link in links:
            # Check final redirected link
            final_link = self.get_final_link(link)
            
            # Check domain of the link
            parsed_link = urlparse(final_link)
            if parsed_link.netloc == "www.flipkart.com":
                final_link += "?affid=flip"
            elif parsed_link.netloc == "www.amazon.in":
                final_link += "?affid=amaz"
            
            # Replace original link with modified link
            msg_text = msg_text.replace(link, final_link)
            
        tm.text = msg_text
        return tm
    
    def find_links(self, text: str) -> list:
        """
        Find all the links in the given text.
        """
        links = []
        words = text.split()
        for word in words:
            if word.startswith("http"):
                links.append(word)
        return links
    
    def get_final_link(self, link: str) -> str:
        """
        Get the final redirected link of the given link.
        """
        try:
            response = requests.get(link, allow_redirects=True)
            final_link = response.url
        except:
            final_link = link
        return final_link
