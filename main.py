from json import dumps
import os

from dotenv import load_dotenv

from utilities.general import recursive_executer
from utilities.scraping import get_wikimapia_links_from_html, iterate_function
from utilities.scraping import GeoScraper, parse_point_to_geoJSON
from utilities.mongo import is_collection, db_connect

if __name__ == '__main__':
    load_dotenv()

    WIKIMAPIA_COUNTRIES_PAGE = os.environ.get('WIKIMAPIA_COUNTRIES_PAGE')
    COUNTRY = os.environ.get('COUNTRY')

    CONNECTION_STRING = os.environ.get('CONNECTION_STRING')
    DATABASE = os.environ.get('DATABASE')

    OUTPUT_FILE = os.environ.get('OUTPUT_FILE')

    

    with open(OUTPUT_FILE, 'w') as file:
        file.write('''{
            "type": "FeatureCollection",
            "features": [
                ''')
                
    
    if is_collection(CONNECTION_STRING, DATABASE, COUNTRY):
        db_connection = db_connect(CONNECTION_STRING, DATABASE, COUNTRY)
        results = db_connection.find({}, projection={'_id': False})
        with open(OUTPUT_FILE, 'a') as file:
            for result in results:
                file.write(dumps(result)+',\n')
        
    else:    
        recursive_executer(get_wikimapia_links_from_html, iterate_function, 2,
                        WIKIMAPIA_COUNTRIES_PAGE+COUNTRY+'/', callback=GeoScraper,
                        connection_string=CONNECTION_STRING, db=DATABASE,
                        collection=COUNTRY, output_file=OUTPUT_FILE)
        

    with open(OUTPUT_FILE, 'a') as file:
        file.write(''']}''')
                