import logging
from typing import Any, Dict

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from tgcf.plugin_models import Replace
from tgcf.plugins import TgcfMessage, TgcfPlugin
from tgcf.utils import replace
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, parse_qs
import re

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
            links= re.findall("(?P<url>https?://[^\s]+)", msg_text)
            for link in links:
                try:
                    # follow redirects to get the final URL
                    options = Options()
                    options.add_argument('--headless')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
                    driver.get(link)
                    final_url = driver.current_url
            
                    driver.close()
                    # parse the URL to get the domain and query parameters
                    parsed_url = urlparse(final_url)
                    domain = parsed_url.netloc
                    query_params = parse_qs(parsed_url.query)
                    # add the affid tag if the domain is flipkart or amazon
                    if domain == "www.flipkart.com":
                        #query_params["affid"] = "saurabhpp1"
                         modified_url =f"{parsed_url.scheme}://{domain}{parsed_url.path}"+'?pid='+query_params["pid"][0]+'&affid=saurabhpp1' #               resp= requests.get(modified_u)
                        #modified_url= resp.json()['response']['shortened_url']
                    elif domain == "www.amazon.in":
                        #query_params["tag"] = 'lootdealsfree-21'
                        modified_url = f"{parsed_url.scheme}://{domain}{parsed_url.path}"+'?tag=lootdealsfree-21'
                    # replace the original link with the modified link in the message text
                    msg_text = msg_text.replace(link, modified_url)
                except:
                    # if there's an error with the link, just move on to the next one
                    pass            
            
            
        tm.text = msg_text
        return tm
