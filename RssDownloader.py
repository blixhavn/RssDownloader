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
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'rss': {
                    'type': 'string'
                },
                'categories': {
                    'type': 'object',
                    'additionalProperties': {
                        'type': 'object',
                        'properties': {
                            'regex': {
                                'type': 'string'
                            },
                            'directory': {
                                'type': 'string'
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
            logging.debug(f"Loading feed: ${feed['rss']}")
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
            logging.debug(f'Parsing category: ${name}')
            processed_items = []
            for i, item in enumerate(items):
                if item is None:
                    continue
                if re.search(re.compile(rules['regex'].lower()), item['title'].lower()):
                    self.save_item(rules['directory'], item['link'])
                    processed_items.append(i)
            for index in processed_items:
                items[index] = None


    def get_title_and_link(self, soup_item):
        try:
            title = soup_item.find('title').get_text()
            link = self.get_link(soup_item)
            return {
                'title': title,
                'link': link
            }
        except AttributeError:
            logging.error('Found malformed item entry')
            return

    def save_item(self, directory, link):
        os.makedirs(directory, exist_ok=True)
        info_req = requests.head(link)
        filename = self.get_filename(info_req)
        full_path = os.path.join(directory, filename)
        if os.path.exists(full_path):
            logging.debug(f'File already downloaded: ${filename}')
            return

        try:
            dl_req = requests.get(link)
        except requests.exceptions.ConnectionError:
            logging.error(f'Could not download file: ${link}')
            return
    
        with open(full_path, 'wb') as f:
            f.write(dl_req.content)
        logging.debug(f'File downloaded: ${filename}')

    def get_filename(self, req):
        url_name = req.url.split('/')[-1]
        cd = req.headers.get('content-disposition')
        if not cd:
            return url_name
        filename = re.findall('filename=(.+)', cd)
        if len(filename) == 0:
            return url_name
        return filename[0].strip('"')

    def get_link(self, soup_item):
        # RSS feeds have different ways of providing the link/url for download.
        # This is an attempt to handle what variations I've found
        link = soup_item.find('link')
        if link:
            return link.get_text()
        
        enclosure = soup_item.find('enclosure')
        if enclosure:
            return enclosure.attrs['url']

        logging.error(
            f"Could not extract download link for ${soup_item.find('title').get_text()}"
        )
        raise AttributeError


@click.command()
@click.option('--debug', is_flag=True)
def main(debug):
    rssDownloader = RssDownloader(debug=debug)
    rssDownloader.readFeeds()

if __name__ == '__main__':
    main()