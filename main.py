from json import dumps
import os

from dotenv import load_dotenv

from utilities.general import recursive_executer
from utilities.scraping import get_wikimapia_links_from_html, iterate_function
from utilities.scraping import GeoScraper
from utilities.mongo import is_collection, db_connect


if __name__ == '__main__':
    # First, the .env file is loaded into the process.
    load_dotenv()

    # Assigning env vars into constants.
    WIKIMAPIA_COUNTRIES_PAGE = os.environ.get('WIKIMAPIA_COUNTRIES_PAGE')
    COUNTRY = os.environ.get('COUNTRY')
    LAYERS = int(os.environ.get('LAYERS'))

    CONNECTION_STRING = os.environ.get('CONNECTION_STRING')
    DATABASE = os.environ.get('DATABASE')

    OUTPUT_FILE = os.environ.get('OUTPUT_FILE')

    # Start writing the output file in geojson format.
    with open(OUTPUT_FILE, 'w') as file:
        file.write('''{
            "type": "FeatureCollection",
            "features": [
                ''')

    # If a collection of the desired country already exists in mongo,
    # it means it was collected before. Instead of rescraping, the db is used
    #  to create the geojson.
    if is_collection(CONNECTION_STRING, DATABASE, COUNTRY):
        db_connection = db_connect(CONNECTION_STRING, DATABASE, COUNTRY)
        results = db_connection.find({}, projection={'_id': False})
        with open(OUTPUT_FILE, 'a') as file:
            for result in results:
                file.write(dumps(result)+',\n')

    # Otherwise, the country's page is scraped. It is needed to get to a deeper
    # layer of the website, so recursion is used.
    # Once getting to a point of interest, it executes to
    # callback function over it, alongside the given kwargs.
    # The callback function will create a geojson from the point of interest
    #  and append it into the output file, and isnert it to the db.
    else:
        recursive_executer(get_wikimapia_links_from_html, iterate_function, LAYERS,
                           WIKIMAPIA_COUNTRIES_PAGE+COUNTRY+'/', callback=GeoScraper,
                           mongo_connection_string=CONNECTION_STRING, db=DATABASE,
                           collection=COUNTRY, output_file=OUTPUT_FILE)

    #  This is needed to close the geojson.
    with open(OUTPUT_FILE, 'a') as file:
        file.write(''']}''')
