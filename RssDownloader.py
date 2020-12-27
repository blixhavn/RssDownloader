import click
import logging
import json
import os
import re
import requests

from jsonschema import validate, ValidationError
from bs4 import BeautifulSoup


class RssDownloader():

    config_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "rss": {
                    "type": "string"
                },
                "categories": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "regex": {
                                "type": "string"
                            },
                            "directory": {
                                "type": "string"
                            }
                        }
                    }
                }
            }
        }
    }

    def __init__(self, debug=False):
        with open('config.json', 'r') as f:
            self.config = json.load(f)
            try:
                validate(instance=self.config, schema=self.config_schema)
            except ValidationError as e:
                logging.error(f'Config is invalid: ${e}')

        log_level = logging.DEBUG if debug else logging.ERROR
        logging.basicConfig(filename='debug.log', level=log_level)

    def readFeeds(self):
        for feed in self.config:
            req = requests.get(feed['rss'])
            if req.status_code != 200:
                logging.error(f"Could not load RSS feed: ${feed['rss']}")
                continue
            xmlsoup = BeautifulSoup(req.content, 'xml')

            self.parseItems(xmlsoup, feed)


    def parseItems(self, xmlsoup, feed):
        itemsoup = xmlsoup.find_all('item')
        items = list(filter(None, map(self.get_title_and_link, itemsoup)))

        for name, rules in feed['categories'].items():
            processed_items = []
            for i, item in enumerate(items):
                if item is None:
                    continue
                if re.search(re.compile(rules['regex']), item['title'].lower()):
                    self.save_item(rules['directory'], item['link'])
                    processed_items.append(i)
            for index in processed_items:
                items[index] = None


    def get_title_and_link(self, soup_item):
        try:
            title = soup_item.find('title').get_text()
            link = soup_item.find('link').get_text()
            return {
                'title': title,
                'link': link
            }
        except AttributeError:
            logging.error("Found malformed item entry")
            return

    def save_item(self, directory, link):
        os.makedirs(directory, exist_ok=True)
        req = requests.get(link)
        filename = self.get_filename(req)
        full_path = os.path.join(directory, filename)
        if os.path.exists(full_path):
            logging.debug(f"File already downloaded: ${filename}")
            return
        with open(full_path, 'wb') as f:
            f.write(req.content)

    def get_filename(self, req):
        url_name = req.url.split('/')[-1]
        cd = req.headers.get('content-disposition')
        if not cd:
            return url_name
        filename = re.findall('filename=(.+)', cd)
        if len(filename) == 0:
            return url_name
        return filename[0].strip('"')


@click.command()
@click.option('--debug', is_flag=True)
def main(name, debug):
    rssDownloader = RssDownloader(debug=debug)
    rssDownloader.readFeeds()

if __name__ == "__main__":
    main()