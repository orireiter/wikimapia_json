import re
import requests
import datetime
from json import dumps
from inspect import isclass

from bs4 import BeautifulSoup as bs
from bs4 import SoupStrainer

from utilities.mongo import db_connect
from utilities.general import iterate_function


def check_last_page(url: str):
    res = requests.get(url)
    if res.status_code != 200:
        print(f'{datetime.datetime.now()} ERROR: Not status code 200 for {url}, did you type a country name correctly?')
        return None
    else:
        return res.text


def get_wikimapia_links_from_html(*url_parts: str):
    '''
        This function is specific to wikimapia,
        and collects a list of links from countries' pages.
        In this project it is iterated over to get points of interest
        since the country / region / district pages use the same template.
    '''

    # Because the use of iteration, parts of the url may be added each time,
    # therefore, it accepts args, and then connects them to a complete url.
    link = ''.join(url_parts)
    page_html = check_last_page(link)
    if not page_html:
        return None

    # soupstrainer is used to instanciate bs4 only with relevant attributes.
    parse_only = SoupStrainer('div', {'class': 'span3'})

    html_object = bs(page_html, 'lxml', parse_only=parse_only)
    return [a['href'] for a in html_object.find_all('a', attrs={'href': True, 'data-url': False})]


class GeoScraper():
    '''
            This class is sort of a specific extension of bs4
            that scrapes points of interest in wikimapia and 
            returns a geojson.

            Attributes
            ----------
            url: str
                A url of an html of a point of interest in wikimapia.
            requests_session: requests.session
                A session used to get the html form the url given.
            
            Methods
            -------
            parse_point_to_geoJSON:
                Takes the html and parses into a dictionary.
            get_geometry:
                This function extracts the coordinates from the html.
            get_properties:
                This function extracts additional properties from the html.
            get_location:
                This function extracts location-related info from the html.
            get_description:
                This function extracts description-related info from the html.
            get_nearby_places:
                This function extracts nearby-related info from the html.
            __call__:
                This function executes parse_point_to_geoJSON,
                appends it to an output file given, and inserts it to mongodb.
        '''
    def __init__(self, url, requests_session, **kwargs):
        res = requests_session.get(url)
        if res.status_code != 200:
            print('Not status code 200.')
            raise Exception(
                f'{datetime.datetime.now()} ERROR: GeoScraper couldn\'t scrape {url}')
        else:
            self.html = res.text

    def __call__(self, mongo_connection_string, db, collection, output_file, eof=False,**kwargs):
        '''
            When an object of this class is used as a callable
            this function will be executed.
            It is specifically made for the task i was given,
            but can be changed easily.
            In my case, it parses the html into a geojson
            and then appends it into a file, and inserts it to  a db
            so the next time a country is asked for, it'll already
            be in the db.
        '''

        geo_json = self.parse_point_to_geoJSON()
        
        if eof:
            eol = '\n'
        else:
            eol = ',\n'

        with open(output_file, 'a') as file:
            file.write(dumps(geo_json)+eol)

        db_connection = db_connect(mongo_connection_string, db, collection)
        db_connection.insert_one(geo_json)

    def parse_point_to_geoJSON(self) -> dict:
        '''
            This function takes the given html and extracts relevant info from it.
            returning it in a json made in geojson format.
        '''

        parse_only = SoupStrainer('div', {'id': 'page-content'})
        html_object = bs(self.html, 'lxml', parse_only=parse_only)

        #----------------------------------------------------------#
        geometry = self.get_geometry(html_object)

        #----------------------------------------------------------#
        properties = self.get_properties(html_object)

        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }

    @staticmethod
    def get_geometry(html_object) -> dict:
        '''
            This function extracts the coordinates from the html.
        '''
        try:
            coordinates = html_object.find(
                'b', text=re.compile('Coordinates')).nextSibling.split()
        except:
            coordinates = []
        finally:
            geometry = {"type": "Point",
                        "coordinates": coordinates}

        return geometry

    def get_properties(self, html_object) -> dict:
        '''
            This function extracts additional properties from the html.
        '''

        location = self.get_location(html_object)

        #----------------------------------------------------------#

        description = self.get_description(html_object)

        #----------------------------------------------------------#

        nearby_places = self.get_nearby_places(html_object)

        return {'location': location,
                'description': description,
                'nearby_places': nearby_places}

    @staticmethod
    def get_location(html_object) -> dict:
        '''
            This function extracts location-related info from the html.
        '''
        
        location = {}

        address = html_object.address.get_text().split()

        location['country'] = address[0]
        location['region'] = address[2]
        location['district'] = address[4]

        return location

    @staticmethod
    def get_description(html_object) -> dict:
        '''
            This function extracts description-related info from the html.
        '''

        description_dict = {}

        description = html_object.find('div', {'id': 'place-description'})
        if description != None:
            description_dict['description'] = description.text.strip()
        else:
            description_dict['description'] = description

        return description_dict

    @staticmethod
    def get_nearby_places(html_object) -> list:
        '''
            This function extracts nearby-related info from the html.
        '''

        nearby_places_list = []
        nearby_places = html_object.find('div', {'id': 'nearby-places'})
        for place in nearby_places.find_all('li'):
            nearby_places_list.append(
                {'name': place.a.text,
                    'distance': place.span.text})

        return nearby_places_list
