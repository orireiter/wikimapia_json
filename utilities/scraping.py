import requests
from json import dump

from bs4 import BeautifulSoup as bs
from bs4 import SoupStrainer


def check_last_page(url: str):
    res = requests.get(url)
    if res.status_code != 200:
        print('Not status code 200, did you type a country name correctly.')
        return None
    else:
        return res.text


def get_wikimapia_links_from_html(*args: str):
    link = ''.join(args)
    page_html = check_last_page(link)
    if not page_html:
        return None

    parse_only = SoupStrainer('div', {'class': 'span3'})

    html_object = bs(page_html, 'lxml', parse_only=parse_only)
    return [a['href'] for a in html_object.find_all('a', attrs={'href': True, 'data-url': False})]


def parse_point_to_geoJSON(urls: list):
    for url in urls:

        res = requests.get(url)

        parse_only = SoupStrainer('div', {'id': 'page-content'})
        html_object = bs(res.text, 'lxml', parse_only=parse_only)

        # print(html_object.find(text='Coordinates:'))

        properties = {}

        address = html_object.address.find_all('a', )
        properties['country'] = address[0].get_text()
        properties['region'] = address[1].get_text()
        properties['district'] = address[2].get_text()

        # print(properties)
