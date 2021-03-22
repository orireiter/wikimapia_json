from utilities.general import recursive_executer
from utilities.scraping import get_wikimapia_links_from_html, parse_point_to_geoJSON


WIKIMAPIA_COUNTRIES_PAGE = 'https://wikimapia.org/country/'


COUNTRY = 'israel'



recursive_executer(get_wikimapia_links_from_html, parse_point_to_geoJSON, 2,
                   WIKIMAPIA_COUNTRIES_PAGE+COUNTRY+'/')
