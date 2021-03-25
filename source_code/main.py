from json import dumps
import os
import datetime
import argparse

from dotenv import load_dotenv

from utilities.general import recursive_executer, iterate_function
from utilities.scraping import get_wikimapia_links_from_html
from utilities.scraping import HTMLGeoScraper, APIGeoScraper
from utilities.mongo import is_collection, db_connect
from utilities.proxy_connection import TorRequests


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='To scrape wikimapia,'
                                     ' specify a country to scrape, a '
                                     'scraping method, and an output file.')
    parser.add_argument('-c', '--country', required=True,
                        type=str, help="A country to scrape.")
    parser.add_argument('-s', '--scrape', required=True, type=str,
                        help="A scraping-source. Either html OR api .")
    parser.add_argument('-o', '--output', required=True, type=str,
                        help="A file to output the data into.")
    args = parser.parse_args()

    country = args.country
    scraping_source = args.scrape
    output_file = args.output

    if scraping_source == 'html':
        scraper = HTMLGeoScraper
    elif scraping_source == 'api':
        scraper = APIGeoScraper
    else:
        raise Exception(f'{datetime.datetime.now()} -> Error: scraping '
                        'source must be either html OR api.')

    # First, the .env file is loaded into the process.
    load_dotenv()

    # Assigning env vars into constants.
    WIKIMAPIA_COUNTRIES_PAGE = os.environ.get('WIKIMAPIA_COUNTRIES_PAGE')
    LAYERS = int(os.environ.get('LAYERS'))

    CONNECTION_STRING = os.environ.get('CONNECTION_STRING')
    DATABASE = os.environ.get('DATABASE')

    TOR_HOST = os.environ.get('TOR_HOST')
    TOR_MANAGEMENT_PORT = int(os.environ.get('TOR_MANAGEMENT_PORT'))
    TOR_MANAGEMENT_PASSWORD = os.environ.get('TOR_MANAGEMENT_PASSWORD')
    TOR_PORT = int(os.environ.get('TOR_PORT'))
    TOR_SWITCH_IP_EVERY = int(os.environ.get('TOR_SWITCH_IP_EVERY'))

    # Start writing the output file in geojson format.
    with open(output_file, 'w') as file:
        file.write('''{
            "type": "FeatureCollection",
            "features": [
                ''')

    # If a collection of the desired country already exists in mongo,
    # it means it was collected before. Instead of rescraping, the db is used
    #  to create the geojson.
    if is_collection(CONNECTION_STRING, DATABASE, country):
        print(f'{datetime.datetime.now()} -> INFO: {country} already in DB,'
              ' retrieving it.')
        db_connection = db_connect(CONNECTION_STRING, DATABASE, country)
        results = db_connection.find({}, projection={'_id': False})
        with open(output_file, 'a') as file:
            for result in results:
                file.write(dumps(result)+',\n')

    # Otherwise, the country's page is scraped. It is needed to get to a deeper
    # layer of the website, so recursion is used.
    # Once getting to a point of interest, it executes to
    # callback function over it, alongside the given kwargs.
    # The callback function will create a geojson from the point of interest
    # and append it into the output file, and insert it to the db.
    # A proxied connection is used to switch IPs and not get blocked.
    else:
        proxied_connection = TorRequests(
            TOR_HOST, TOR_MANAGEMENT_PORT, TOR_MANAGEMENT_PASSWORD, TOR_PORT, TOR_SWITCH_IP_EVERY)
        print(f'{datetime.datetime.now()} -> INFO: {country} not in db,'
              ' starting to scrape.')
        recursive_executer(get_wikimapia_links_from_html,
                           iterate_function,
                           LAYERS,
                           WIKIMAPIA_COUNTRIES_PAGE+country+'/',
                           callback=scraper,
                           mongo_connection_string=CONNECTION_STRING,
                           db=DATABASE,
                           collection=country,
                           output_file=output_file,
                           requests_session=proxied_connection)

    #  This is needed to close the geojson.
    with open(output_file, 'a') as file:
        file.write('''{
            "type": null,
            "geometry": {
                "type": null,
                "coordinates": []
            },
            "properties": {
                "location": {
                    "country": null,
                    "region": null,
                    "district": null
                },
                "description": {
                    "description": null
                },
                "nearby_places": []
            }
            }
        ]}''')

    print(f'{datetime.datetime.now()} -> INFO: Done scraping {country}!')
