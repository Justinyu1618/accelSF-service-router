import pprint
import re
import requests
from bs4 import BeautifulSoup
import argparse
from bs4.element import Comment


RE_BASE_URL = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\=]*)'
RE_MAILTO_URL = r'mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


class WebsiteParser:
    def __init__(self, url):
        self.url = url
        self.page = requests.get(url)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')

        baseUrl = re.match(RE_BASE_URL, url)
        if (not baseUrl):
            raise Exception("invalid url")
        self.baseUrl = baseUrl.group(0)

    def parse(self):
        all_text = self.extract_text()
        links = self.extract_links()

        return {
            "text": all_text,
            "links": links
        }

    def extract_text(self):
        texts = self.soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts)
        return u" ".join(t.strip() for t in visible_texts)

    def extract_links(self):
        links = []
        for link in self.soup.find_all('a'):
            links.append(link.get('href'))
        return self.classify_links(links)

    def classify_links(self, links):
        internal_links = []
        external_links = []
        emails = []

        for link in links:
            url_match = re.match(RE_BASE_URL, link)
            mailto_match = re.match(RE_MAILTO_URL, link)
            if url_match:
                if url_match.group(0) == self.baseUrl:
                    internal_links.append(link)
                else:
                    external_links.append(link)
            elif mailto_match:
                emails.append(mailto_match.group(1))

        return {
            "internal": internal_links,
            "external": external_links,
            "emails": emails
        }


if __name__ == '__main__':
    printer = pprint.PrettyPrinter(indent=4)
    argparser = argparse.ArgumentParser()
    argparser.add_argument("url", help="url to scrape")
    args = argparser.parse_args()

    web_parser = WebsiteParser(args.url)

    parsed = web_parser.parse()
    printer.pprint(parsed)
