from time import time

from utilities.general import recursive_executer
from utilities.scraping import get_wikimapia_links_from_html, iterate_function
from utilities.scraping import GeoScraper, parse_point_to_geoJSON


WIKIMAPIA_COUNTRIES_PAGE = 'https://wikimapia.org/country/'
COUNTRY = 'israel'

CONNECTION_STRING = 'localhost:27017'
DATABASE = 'countries'


if __name__ == '__main__':

    start = time()
    recursive_executer(get_wikimapia_links_from_html, iterate_function, 2,
                       WIKIMAPIA_COUNTRIES_PAGE+COUNTRY+'/', callback=GeoScraper,
                       connection_string=CONNECTION_STRING, db=DATABASE,
                       collection=COUNTRY)
    end = time()
    print('runtime is -> ', end-start)
