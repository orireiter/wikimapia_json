import requests

from bs4 import BeautifulSoup as bs
from bs4 import SoupStrainer

WIKIMAPIA_COUNTRIES_PAGE = 'https://wikimapia.org/country/'


COUNTRY = 'canada'


def check_country(country: str) -> bool:
    res = requests.get(WIKIMAPIA_COUNTRIES_PAGE+country)
    if res.status_code != 200:
        print('Not status code 200, did you type a country name correctly.')
        return None
    else:
        return res.text


def get_regions(country: str) -> callable:
    country_html = check_country(country)
    if not country_html:
        return None

    parse_only = SoupStrainer('div', {'class': 'span3'})
    # parse_only = SoupStrainer('li')

    html_object = bs(country_html, 'lxml', parse_only=parse_only)
    print(html_object.find_all('a'))

    parse_only1 = SoupStrainer('a')
    second = bs(html_object.__copy__().encode(
        'utf-8'), 'lxml', parse_only=parse_only1)
    print('\n\n\n', second)
    print(second.children)
    # for a in second.children:
    #     print(a.name)


get_regions(COUNTRY)
