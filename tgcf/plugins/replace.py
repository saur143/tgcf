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
        msg_text = re.findall("(?P<url>https?://[^\s]+)", msg_text)
        for link in msg_text:
            try:
                # follow redirects to get the final URL
                response = requests.head(link, allow_redirects=True)
                final_url = response.url
                
                # parse the URL to get the domain and query parameters
                parsed_url = urlparse(final_url)
                domain = parsed_url.netloc
                query_params = parse_qs(parsed_url.query)
                
                # add the affid tag if the domain is flipkart or amazon
                if domain == "www.flipkart.com":
                    query_params["affid"] = "saurabhpp1"
                elif domain == "www.amazon.in":
                    query_params["tag"] = "lootdealsfree-21"
                
                # construct the modified URL
                modified_url = f"{parsed_url.scheme}://{domain}{parsed_url.path}"
                if query_params:
                    modified_url += "?" + "&".join([f"{key}={value[0]}" for key, value in query_params.items()])
                
                # replace the original link with the modified link in the message text
                msg_text = msg_text.replace(link, modified_url)
            except:
                # if there's an error with the link, just move on to the next one
                pass
                
        tm.text = msg_text
        return tm
